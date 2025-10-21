"""Consolidate legacy material logs into the single source of truth."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

REPAIR_MATERIAL_DOCTYPE = "Repair Material Movement"
LEGACY_DOCTYPES = (
    "Repair Parts Used",
    "Material Use Log",
)


def _migrate_row(row: dict) -> None:
    exists = frappe.db.exists(
        REPAIR_MATERIAL_DOCTYPE,
        {
            "repair_order": row.get("repair_order"),
            "item_code": row.get("item_code"),
            "serial_no": row.get("serial_no"),
            "movement_type": row.get("movement_type") or "Issue",
        },
    )
    if exists:
        return
    doc = frappe.get_doc(
        {
            "doctype": REPAIR_MATERIAL_DOCTYPE,
            "repair_order": row.get("repair_order"),
            "item_code": row.get("item_code"),
            "warehouse": row.get("warehouse"),
            "serial_no": row.get("serial_no"),
            "qty": row.get("qty") or row.get("quantity") or 0,
            "movement_type": row.get("movement_type") or "Issue",
            "posting_datetime": now_datetime(),
        }
    )
    doc.flags.ignore_permissions = True
    doc.insert()


def execute() -> None:
    if not frappe.db.table_exists(REPAIR_MATERIAL_DOCTYPE):
        return

    for doctype in LEGACY_DOCTYPES:
        if not frappe.db.table_exists(doctype):
            continue
        rows = frappe.db.get_all(
            doctype,
            fields=[
                "name",
                "parent",
                "repair_order",
                "item_code",
                "warehouse",
                "serial_no",
                "qty",
                "quantity",
                "movement_type",
            ],
        )
        for row in rows:
            try:
                _migrate_row(row)
            except Exception:
                frappe.log_error(
                    "Failed to migrate material row", frappe.as_json({"doctype": doctype, "row": row})
                )
        if frappe.db.has_column(doctype, "docstatus"):
            frappe.db.sql(f"update `tab{doctype}` set docstatus = 2")
