"""Static audit tool for validating Python imports within the repair_portal package."""

from __future__ import annotations

import ast
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set

APP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = APP_ROOT.parent
sys.path.insert(0, str(REPO_ROOT))

SKIP_DIRS: Set[str] = {".git", "node_modules", "public", "dist", "build", "__pycache__"}
ALLOWED_EXTERNAL_PREFIXES: tuple[str, ...] = (
    "frappe",
    "erpnext",
    "pandas",
    "numpy",
    "dateutil",
    "requests",
    "bleach",
    "validators",
    "matplotlib",
    "librosa",
    "soundfile",
    "cv2",
    "reportlab",
    "PIL",
    "pdf2image",
    "pytesseract",
    "regex",
)


@dataclass
class ImportIssue:
    module: str
    file: Path
    lineno: int
    message: str

    def __str__(self) -> str:  # pragma: no cover - human readable formatting
        rel_path = self.file.relative_to(REPO_ROOT)
        return f"{rel_path}:{self.lineno}: {self.message} ({self.module})"


def iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def module_name_from_path(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def resolve_from_import(module_name: str, node: ast.ImportFrom) -> str | None:
    package = module_name.rsplit(".", 1)[0] if "." in module_name else module_name
    target = ("." * node.level) + (node.module or "")
    if not target:
        target = "."
    try:
        resolved = importlib.util.resolve_name(target, package or module_name)
    except (ImportError, ValueError):
        return None
    return resolved


def spec_exists(module: str) -> bool:
    if module.startswith(ALLOWED_EXTERNAL_PREFIXES):
        return True
    try:
        spec = importlib.util.find_spec(module)
    except (ImportError, ModuleNotFoundError):
        return False
    return spec is not None


def audit_file(path: Path) -> List[ImportIssue]:
    issues: List[ImportIssue] = []
    module_name = module_name_from_path(path)
    try:
        tree = ast.parse(path.read_text(), type_comments=True)
    except SyntaxError as exc:
        issues.append(
            ImportIssue(
                module=module_name,
                file=path,
                lineno=getattr(exc, "lineno", 0) or 0,
                message=f"Syntax error during AST parse: {exc.msg}",
            )
        )
        return issues

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if not spec_exists(name):
                    issues.append(
                        ImportIssue(
                            module=name,
                            file=path,
                            lineno=node.lineno,
                            message="Unresolved import",
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            base = resolve_from_import(module_name, node)
            if base and not spec_exists(base):
                issues.append(
                    ImportIssue(
                        module=base,
                        file=path,
                        lineno=node.lineno,
                        message="Unresolved import base",
                    )
                )
            elif not base:
                issues.append(
                    ImportIssue(
                        module=node.module or "",
                        file=path,
                        lineno=node.lineno,
                        message="Unable to resolve relative import",
                    )
                )
    return issues


def main() -> None:
    issues: List[ImportIssue] = []
    for file in iter_python_files(REPO_ROOT / "repair_portal"):
        issues.extend(audit_file(file))

    if issues:
        print("❌ Python import audit failed:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)

    print("✅ Python import audit passed")


if __name__ == "__main__":
    main()
