"""Static audit tool for validating JavaScript and Vue import paths."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable, List, Set

REPO_ROOT = Path(__file__).resolve().parents[1]
JS_EXTENSIONS = ["", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".json"]
SKIP_DIRS: Set[str] = {".git", "node_modules", "dist", "build", "public/dist"}
BUNDLE_ROOT = REPO_ROOT / "public" / "js"

IMPORT_RE = re.compile(r"import\s+(?:[^'\"]+?\s+from\s+)?['\"]([^'\"]+)['\"]")
DYNAMIC_IMPORT_RE = re.compile(r"import\(['\"]([^'\"]+)['\"]\)")
REQUIRE_RE = re.compile(r"require\(['\"]([^'\"]+)['\"]\)")
FRAPPE_REQUIRE_RE = re.compile(r"frappe\.require\(['\"]([^'\"]+)['\"]\)")


class ImportIssue:
    def __init__(self, file: Path, specifier: str, message: str) -> None:
        self.file = file
        self.specifier = specifier
        self.message = message

    def __str__(self) -> str:  # pragma: no cover - formatting helper
        rel_path = self.file.relative_to(REPO_ROOT)
        return f"{rel_path}: {self.specifier} -> {self.message}"


def iter_js_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_dir():
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            continue
        if path.suffix.lower() not in {".js", ".vue", ".mjs", ".cjs", ".ts", ".tsx"}:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def resolve_relative(file: Path, spec: str) -> bool:
    base = (file.parent / spec).resolve()
    if base.exists():
        return True
    for ext in JS_EXTENSIONS:
        candidate = file.parent / f"{spec}{ext}"
        if candidate.exists():
            return True
    # Directory index resolution
    for ext in ("index.js", "index.ts", "index.vue", "index.mjs", "index.tsx"):
        candidate = base / ext
        if candidate.exists():
            return True
    return False


def bundle_exists(spec: str) -> bool:
    matches = list(BUNDLE_ROOT.rglob(spec))
    return bool(matches)


def audit_file(path: Path) -> List[ImportIssue]:
    issues: List[ImportIssue] = []
    source = path.read_text(encoding="utf-8")
    specs = set()
    for pattern in (IMPORT_RE, DYNAMIC_IMPORT_RE, REQUIRE_RE, FRAPPE_REQUIRE_RE):
        for match in pattern.finditer(source):
            specs.add(match.group(1))

    for spec in specs:
        if spec.startswith(('.', '..')):
            if not resolve_relative(path, spec):
                issues.append(ImportIssue(path, spec, "Missing relative target"))
        elif spec.endswith(".bundle.js"):
            if not bundle_exists(spec):
                issues.append(ImportIssue(path, spec, "Bundle not found under public/js"))
        else:
            # Treat bare module specifiers as external dependencies
            continue
    return issues


def main() -> None:
    issues: List[ImportIssue] = []
    for file in iter_js_files(REPO_ROOT):
        issues.extend(audit_file(file))

    if issues:
        print("❌ JS import audit failed:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)

    print("✅ JS import audit passed")


if __name__ == "__main__":
    main()
