"""Generate a cross-module inventory for the repair_portal bench."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[2]
APP_NAME = "repair_portal"
APP_ROOT = ROOT / APP_NAME
BUILD_DIR = ROOT / ".build"
OUTPUT_PATH = BUILD_DIR / "cross_module_map.json"


@dataclass
class FieldInfo:
    fieldname: str
    fieldtype: str
    options: Optional[str]
    reqd: int


@dataclass
class DocTypeInfo:
    name: str
    module: str
    path: str
    is_child_table: bool
    autoname: Optional[str]
    naming_rule: Optional[str]
    indexes: List[str]
    fields: List[FieldInfo]


@dataclass
class ScriptInfo:
    path: str
    doctype: Optional[str] = None
    script_type: Optional[str] = None


@dataclass
class HookInfo:
    name: str
    kind: str
    value: str


@dataclass
class WhitelistedMethod:
    dotted_path: str
    roles: List[str]


@dataclass
class CodebaseInventory:
    doctypes: List[DocTypeInfo]
    client_scripts: List[ScriptInfo]
    controllers: List[ScriptInfo]
    reports: List[ScriptInfo]
    pages: List[ScriptInfo]
    workspaces: List[ScriptInfo]
    hooks: List[HookInfo]
    whitelisted_methods: List[WhitelistedMethod]


def _iter_doctype_json() -> Iterable[Path]:
    for path in APP_ROOT.rglob("*.json"):
        if "/doctype/" in path.as_posix() and path.name != "dashboard_chart.json":
            yield path


def _collect_doctypes() -> List[DocTypeInfo]:
    doctypes: List[DocTypeInfo] = []
    for path in sorted(_iter_doctype_json()):
        data = json.loads(path.read_text())
        name = data.get("name") or data.get("doctype")
        fields = [
            FieldInfo(
                fieldname=field.get("fieldname"),
                fieldtype=field.get("fieldtype"),
                options=field.get("options"),
                reqd=field.get("reqd", 0),
            )
            for field in data.get("fields", [])
        ]
        doctypes.append(
            DocTypeInfo(
                name=name,
                module=data.get("module", ""),
                path=str(path.relative_to(ROOT)),
                is_child_table=bool(data.get("istable")),
                autoname=data.get("autoname"),
                naming_rule=data.get("naming_rule"),
                indexes=data.get("indexes", []),
                fields=fields,
            )
        )
    return doctypes


def _collect_scripts(pattern: str) -> List[ScriptInfo]:
    scripts: List[ScriptInfo] = []
    for path in sorted(APP_ROOT.rglob(pattern)):
        rel_path = path.relative_to(ROOT)
        doctype = None
        if "/doctype/" in path.as_posix():
            doctype = path.parent.name.replace("_", " ")
        scripts.append(ScriptInfo(path=str(rel_path), doctype=doctype))
    return scripts


def _collect_hooks() -> List[HookInfo]:
    hooks_path = APP_ROOT / "hooks.py"
    hooks: List[HookInfo] = []
    if not hooks_path.exists():
        return hooks

    source = hooks_path.read_text()
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    value_repr = ast.get_source_segment(source, node.value) or ""
                    hooks.append(
                        HookInfo(name=target.id, kind=node.value.__class__.__name__, value=value_repr)
                    )
    return hooks


class WhitelistVisitor(ast.NodeVisitor):
    def __init__(self, module_path: str) -> None:
        self.module_path = module_path
        self.methods: List[WhitelistedMethod] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        decorators = node.decorator_list
        whitelisted = any(
            (isinstance(decorator, ast.Attribute) and decorator.attr == "whitelist")
            or (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "whitelist"
            )
            or (isinstance(decorator, ast.Name) and decorator.id == "whitelist")
            for decorator in decorators
        )

        roles: List[str] = []
        for decorator in decorators:
            if isinstance(decorator, ast.Call) and getattr(decorator.func, "id", "") == "require_roles":
                for arg in decorator.args:
                    if isinstance(arg, (ast.Tuple, ast.List)):
                        for elt in arg.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                roles.append(elt.value)
                for keyword in decorator.keywords:
                    if isinstance(keyword.value, (ast.Tuple, ast.List)):
                        for elt in keyword.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                roles.append(elt.value)
        if whitelisted:
            dotted_path = f"{self.module_path}.{node.name}".strip(".")
            self.methods.append(WhitelistedMethod(dotted_path=dotted_path, roles=roles))
        self.generic_visit(node)


def _collect_whitelisted_methods() -> List[WhitelistedMethod]:
    methods: List[WhitelistedMethod] = []
    for path in APP_ROOT.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        source = path.read_text()
        module = ".".join((APP_NAME,) + path.relative_to(ROOT).with_suffix("").parts)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        visitor = WhitelistVisitor(module)
        visitor.visit(tree)
        methods.extend(visitor.methods)
    return methods


def build_inventory() -> CodebaseInventory:
    doctypes = _collect_doctypes()
    client_scripts = _collect_scripts("*.js")
    controllers = _collect_scripts("*.py")
    reports = _collect_scripts("*.report.json")
    pages = _collect_scripts("*.page.js")
    workspaces = _collect_scripts("*.workspace.json")
    hooks = _collect_hooks()
    whitelisted_methods = _collect_whitelisted_methods()
    return CodebaseInventory(
        doctypes=doctypes,
        client_scripts=client_scripts,
        controllers=controllers,
        reports=reports,
        pages=pages,
        workspaces=workspaces,
        hooks=hooks,
        whitelisted_methods=whitelisted_methods,
    )


def main() -> None:
    BUILD_DIR.mkdir(exist_ok=True)
    inventory = build_inventory()
    serialized = json.dumps(asdict(inventory), default=lambda o: o.__dict__, indent=2)
    OUTPUT_PATH.write_text(serialized)


if __name__ == "__main__":
    main()
