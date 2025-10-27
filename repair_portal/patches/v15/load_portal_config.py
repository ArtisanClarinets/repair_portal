"""Load workflow, notification, and print format fixtures."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import frappe
from frappe.modules.import_file import import_file_by_path


def execute() -> None:
    for path in _iter_json("repair_portal", "repair_portal", "repair_portal", "workflow"):
        _import_if_missing(path)
    for path in _iter_json("repair_portal", "repair_portal", "repair_portal", "notification"):
        _import_if_missing(path)
    for path in _iter_json("repair_portal", "repair_portal", "print_format"):
        _import_if_missing(path)


def _iter_json(*parts: str) -> Iterable[Path]:
    base = Path(frappe.get_app_path(*parts))
    if not base.exists():
        return []
    if base.is_file():
        return [base]
    return [path for path in base.rglob("*.json") if path.is_file()]


def _import_if_missing(path: Path) -> None:
    doc = frappe.parse_json(path.read_text())
    doctype = doc.get("doctype")
    name = doc.get("name")
    if not doctype or not name:
        return
    if frappe.db.exists(doctype, name):
        return
    import_file_by_path(path.as_posix(), force=True, ignore_version=True)
