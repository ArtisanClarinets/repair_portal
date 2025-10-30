#!/usr/bin/env python3
"""Generate operational documentation assets for the repair_portal app.

This helper builds a repository inventory JSON/Markdown summary that lists
modules, DocTypes, pages, reports, web assets, hooks, and fixtures. It is
designed to run without requiring a Frappe bench context.
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

APP_ROOT = Path(__file__).resolve().parents[1]
OPS_ROOT = APP_ROOT / "OPS"


class HookParser(ast.NodeVisitor):
    """Parse hook assignments from hooks.py without executing imports."""

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
                # Unsupported literal structure; skip rather than fail.
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
        raise ValueError(f"Unsupported literal structure: {ast.dump(node, maxlen=200)}")


def read_modules(modules_file: Path) -> List[str]:
    if not modules_file.exists():
        return []
    return [line.strip() for line in modules_file.read_text().splitlines() if line.strip()]


def collect_docfiles(pattern: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for json_path in APP_ROOT.glob(pattern):
        if not json_path.is_file():
            continue
        try:
            data = json.loads(json_path.read_text())
        except json.JSONDecodeError:
            continue
        entry = {
            "name": data.get("name"),
            "module": data.get("module"),
            "doctype": data.get("doctype") or data.get("doc_type"),
            "path": str(json_path.relative_to(APP_ROOT)),
        }
        results.append(entry)
    return sorted(results, key=lambda item: (item.get("module") or "", item.get("name") or ""))


def collect_doctypes() -> List[Dict[str, Any]]:
    return collect_docfiles("**/doctype/*/*.json")


def collect_pages() -> List[Dict[str, Any]]:
    desk_pages = collect_docfiles("**/page/*/*.json")
    portal_pages = []
    for path in (APP_ROOT / "repair_portal" / "www").glob("*.py"):
        portal_pages.append(
            {
                "name": path.stem,
                "module": "www",
                "doctype": None,
                "path": str(path.relative_to(APP_ROOT)),
            }
        )
    return desk_pages + sorted(portal_pages, key=lambda item: item["name"])


def collect_reports() -> List[Dict[str, Any]]:
    return collect_docfiles("**/report/*/*.json")


def collect_web_assets() -> Dict[str, List[str]]:
    assets: Dict[str, List[str]] = {}
    public_root = APP_ROOT / "repair_portal" / "public"
    if not public_root.exists():
        return assets
    for path in public_root.rglob("*"):
        if path.is_file():
            rel = str(path.relative_to(APP_ROOT))
            suffix = path.suffix or "misc"
            assets.setdefault(suffix, []).append(rel)
    for ext in assets:
        assets[ext].sort()
    return assets


def parse_hooks() -> Dict[str, Any]:
    hook_file = APP_ROOT / "repair_portal" / "hooks.py"
    if not hook_file.exists():
        return {}
    tree = ast.parse(hook_file.read_text())
    parser = HookParser()
    parser.visit(tree)
    keys = [
        "app_name",
        "app_title",
        "required_apps",
        "fixtures",
        "doc_events",
        "scheduler_events",
        "before_install",
        "after_install",
        "after_migrate",
    ]
    return {key: parser.assignments.get(key) for key in keys if key in parser.assignments}


def build_inventory() -> Dict[str, Any]:
    inventory = {
        "modules": read_modules(APP_ROOT / "modules.txt"),
        "doctypes": collect_doctypes(),
        "pages": collect_pages(),
        "reports": collect_reports(),
        "web_assets": collect_web_assets(),
        "hooks": parse_hooks(),
    }
    fixtures = inventory["hooks"].get("fixtures") if inventory["hooks"] else None
    inventory["fixtures"] = fixtures or []
    return inventory


def write_inventory_files(inventory: Dict[str, Any]) -> None:
    OPS_ROOT.mkdir(exist_ok=True)
    json_path = OPS_ROOT / "INVENTORY.json"
    json_path.write_text(json.dumps(inventory, indent=2, sort_keys=True))

    md_lines = ["# Repository Inventory", ""]
    md_lines.append("## Modules")
    for module in inventory.get("modules", []):
        md_lines.append(f"- {module}")

    md_lines.append("\n## DocTypes")
    for doctype in inventory.get("doctypes", []):
        md_lines.append(
            f"- **{doctype.get('name')}** (Module: {doctype.get('module')}) — {doctype.get('path')}"
        )

    md_lines.append("\n## Pages")
    for page in inventory.get("pages", []):
        md_lines.append(
            f"- **{page.get('name')}** (Module: {page.get('module')}) — {page.get('path')}"
        )

    md_lines.append("\n## Reports")
    for report in inventory.get("reports", []):
        md_lines.append(
            f"- **{report.get('name')}** (Module: {report.get('module')}) — {report.get('path')}"
        )

    md_lines.append("\n## Web Assets (grouped by extension)")
    for ext, files in sorted(inventory.get("web_assets", {}).items()):
        md_lines.append(f"- **{ext}**")
        for file_path in files:
            md_lines.append(f"  - {file_path}")

    md_lines.append("\n## Hooks")
    for key, value in inventory.get("hooks", {}).items():
        md_lines.append(f"- **{key}**: {json.dumps(value, ensure_ascii=False)}")

    md_lines.append("\n## Fixtures")
    fixtures = inventory.get("fixtures", [])
    if fixtures:
        for fixture in fixtures:
            md_lines.append(f"- {json.dumps(fixture, ensure_ascii=False)}")
    else:
        md_lines.append("- None")

    (OPS_ROOT / "INVENTORY.md").write_text("\n".join(md_lines) + "\n")


def main() -> int:
    inventory = build_inventory()
    write_inventory_files(inventory)
    return 0


if __name__ == "__main__":
    sys.exit(main())
