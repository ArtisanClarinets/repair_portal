"""Ensure naming series and unique constraints across repair modules."""

from __future__ import annotations

from typing import Iterable

import frappe

SERIES = {
    "Repair Order": "RO-.####",
    "Repair Warranty Adjustment": "RWA-.####",
    "Repair QA Outcome": "RQAO-.####",
    "Repair Material Movement": "RMM-.######",
}


def _ensure_series(doctype: str, prefix: str) -> None:
    if not frappe.db.exists("Series", prefix):
        frappe.db.sql("INSERT INTO `tabSeries` (name, current) VALUES (%s, %s)", (prefix, 0))
    frappe.db.set_value("DocType", doctype, "autoname", f"naming_series:{prefix}")


def _ensure_unique_index(doctype: str, fields: Iterable[str], index_name: str) -> None:
    if not frappe.db.has_index(doctype, index_name):
        frappe.db.add_index(doctype, fields, index_name=index_name, unique=True)


def execute() -> None:
    for doctype, prefix in SERIES.items():
        try:
            _ensure_series(doctype, prefix)
        except Exception:
            frappe.log_error("Failed to ensure naming series", frappe.as_json({"doctype": doctype, "prefix": prefix}))

    _ensure_unique_index(
        "Repair Material Movement",
        ["repair_order", "item_code", "serial_no", "movement_type", "posting_datetime"],
        "uniq_repair_material_movement",
    )
