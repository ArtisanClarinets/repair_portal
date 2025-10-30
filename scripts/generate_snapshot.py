#!/usr/bin/env python3
"""Generate operational snapshot documentation for the repair_portal app."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

APP_ROOT = Path(__file__).resolve().parents[1]
OPS_ROOT = APP_ROOT / "OPS"


class HookParser(ast.NodeVisitor):
    """Parse minimal hook assignments from hooks.py."""

    def __init__(self) -> None:
        self.assignments: Dict[str, Any] = {}

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: D401 - ast override
        if len(node.targets) != 1:
            return
        target = node.targets[0]
        if isinstance(target, ast.Name):
            try:
                self.assignments[target.id] = self._literal_eval(node.value)
            except ValueError:
                pass

    def _literal_eval(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [self._literal_eval(el) for el in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(self._literal_eval(el) for el in node.elts)
        if isinstance(node, ast.Dict):
            return {
                self._literal_eval(key): self._literal_eval(value)
                for key, value in zip(node.keys, node.values)
            }
        if isinstance(node, ast.Set):
            return {self._literal_eval(el) for el in node.elts}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self._literal_eval(node.operand)  # type: ignore[arg-type]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._literal_eval(node.left)
            right = self._literal_eval(node.right)
            if isinstance(left, str) and isinstance(right, str):
                return left + right
        raise ValueError("Unsupported literal structure")


def parse_hooks() -> Dict[str, Any]:
    hook_file = APP_ROOT / "repair_portal" / "hooks.py"
    if not hook_file.exists():
        return {}
    parser = HookParser()
    parser.visit(ast.parse(hook_file.read_text()))
    keys = [
        "required_apps",
        "scheduler_events",
    ]
    return {key: parser.assignments.get(key) for key in keys if key in parser.assignments}


class WhitelistCollector(ast.NodeVisitor):
    """Collect whitelisted function names along with their modules."""

    def __init__(self, module_path: Path) -> None:
        self.module_path = module_path
        self.items: List[Tuple[str, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: D401
        if any(self._is_whitelist_decorator(dec) for dec in node.decorator_list):
            dotted_path = f"{self.module_path.stem}.{node.name}"
            self.items.append((node.name, dotted_path))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: D401
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    @staticmethod
    def _is_whitelist_decorator(dec: ast.AST) -> bool:
        if isinstance(dec, ast.Attribute):
            return (
                isinstance(dec.value, ast.Name)
                and dec.value.id == "frappe"
                and dec.attr == "whitelist"
            )
        if isinstance(dec, ast.Call):
            return WhitelistCollector._is_whitelist_decorator(dec.func)
        return False


def get_python_version() -> str:
    return sys.version.split(" ")[0]


def get_node_version() -> str:
    try:
        output = subprocess.check_output(["node", "--version"], stderr=subprocess.STDOUT)
        return output.decode().strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Unavailable (node binary not found during generation)"


def get_package_versions() -> Dict[str, Optional[str]]:
    pyproject = APP_ROOT / "pyproject.toml"
    frappe_version: Optional[str] = None
    erpnext_version: Optional[str] = None
    if pyproject.exists():
        content = pyproject.read_text().splitlines()
        for line in content:
            line = line.split("#", 1)[0]
            if "frappe" in line and "~=" in line:
                frappe_version = line.strip().split("~=")[-1].strip('"')
            if "erpnext" in line and "~=" in line:
                erpnext_version = line.strip().split("~=")[-1].strip('"')
    package_json = APP_ROOT / "package.json"
    node_deps: Dict[str, str] = {}
    if package_json.exists():
        parsed = json.loads(package_json.read_text())
        for key in ("dependencies", "devDependencies"):
            for dep, version in parsed.get(key, {}).items():
                if dep.lower() in {"frappe", "erpnext"}:
                    node_deps[dep] = version
    return {
        "frappe": frappe_version,
        "erpnext": erpnext_version,
        "node_frappelib": node_deps.get("frappe"),
        "node_erpnext": node_deps.get("erpnext"),
    }


def collect_whitelisted_functions() -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for path in (APP_ROOT / "repair_portal").rglob("*.py"):
        if path.name == "__init__.py":
            continue
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        collector = WhitelistCollector(path)
        collector.visit(tree)
        for name, dotted in collector.items:
            results.append({"function": name, "module": dotted, "path": str(path.relative_to(APP_ROOT))})
    results.sort(key=lambda item: item["module"])
    return results


def collect_permission_hooks() -> List[Dict[str, str]]:
    keywords = {"has_permission", "get_permission_query_conditions"}
    results: List[Dict[str, str]] = []
    for path in (APP_ROOT / "repair_portal").rglob("*.py"):
        if path.name == "__init__.py":
            continue
        text = path.read_text()
        for keyword in keywords:
            if keyword in text:
                results.append({"path": str(path.relative_to(APP_ROOT)), "keyword": keyword})
    results.sort(key=lambda item: (item["path"], item["keyword"]))
    return results


def build_snapshot() -> str:
    hooks = parse_hooks()
    whitelisted = collect_whitelisted_functions()
    perm_hooks = collect_permission_hooks()
    versions = get_package_versions()
    python_version = get_python_version()
    node_version = get_node_version()

    lines: List[str] = ["# Safety Snapshot", ""]
    lines.append("## Platform Versions")
    lines.append(f"- Python: `{python_version}`")
    lines.append(f"- Node: `{node_version}`")
    lines.append(
        f"- Frappe (pyproject): `{versions.get('frappe') or 'Managed by bench (not pinned)'}`"
    )
    lines.append(
        f"- ERPNext (pyproject): `{versions.get('erpnext') or 'Managed by bench (not pinned)'}`"
    )
    if versions.get("node_frappelib") or versions.get("node_erpnext"):
        lines.append(
            f"- Node packages: {json.dumps({k: v for k, v in versions.items() if k.startswith('node_') and v})}"
        )
    required_apps = hooks.get("required_apps") if hooks else None
    if required_apps:
        lines.append(f"- Required Apps: {', '.join(required_apps)}")

    lines.append("\n## Scheduler Events")
    scheduler = hooks.get("scheduler_events") if hooks else {}
    if scheduler:
        for cadence, events in scheduler.items():
            lines.append(f"- **{cadence}**:")
            for event in events:
                lines.append(f"  - `{event}`")
    else:
        lines.append("- None configured")

    lines.append("\n## Whitelisted Endpoints")
    if whitelisted:
        for item in whitelisted:
            lines.append(f"- `{item['module']}` — {item['path']}")
    else:
        lines.append("- No `frappe.whitelist` endpoints detected")

    lines.append("\n## Permission-Sensitive Implementations")
    if perm_hooks:
        for item in perm_hooks:
            lines.append(f"- `{item['keyword']}` defined in {item['path']}")
    else:
        lines.append("- No custom permission hooks detected")

    lines.append("\n## Website / Portal Exposure Risks")
    lines.append(
        "- Portal routes located under `repair_portal/www`. Review ownership enforcement in controllers such as `repair_pulse.py` and ensure DocType permissions prevent cross-customer data leaks."
    )
    lines.append(
        "- Evaluate whitelisted APIs for CSRF protection and ownership checks before exposing additional portal functionality."
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    OPS_ROOT.mkdir(exist_ok=True)
    snapshot = build_snapshot()
    (OPS_ROOT / "SNAPSHOT.md").write_text(snapshot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
