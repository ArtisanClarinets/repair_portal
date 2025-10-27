from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

from repair_portal.utils import barcode


BENCH_NAME = "Primary Bench"


def execute() -> None:
    _ensure_sales_invoice_field()
    _ensure_default_bench()
    _backfill_barcodes("Instrument", barcode.ensure_instrument_barcode)
    _backfill_barcodes("Clarinet Intake", barcode.ensure_clarinet_intake_barcode)
    _backfill_barcodes("Repair Order", barcode.ensure_repair_order_barcode)
    _backfill_reservation_types()


def _ensure_sales_invoice_field() -> None:
    if frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": "repair_order"}):
        return
    create_custom_field(
        "Sales Invoice",
        {
            "fieldname": "repair_order",
            "label": "Repair Order",
            "fieldtype": "Link",
            "options": "Repair Order",
            "insert_after": "customer",
        },
        ignore_validate=True,
    )


def _ensure_default_bench() -> None:
    if frappe.db.exists("Bench", BENCH_NAME):
        return
    doc = frappe.new_doc("Bench")
    doc.name = BENCH_NAME
    doc.location = "Main"
    try:
        doc.insert(ignore_permissions=True)
    except Exception:
        frappe.db.rollback()


def _backfill_barcodes(doctype: str, handler) -> None:
    names = frappe.get_all(doctype, fields=["name"], limit=5000)
    for row in names:
        doc = frappe.get_doc(doctype, row.name)
        handler(doc)
        if doc.get("barcode"):
            frappe.db.set_value(doctype, doc.name, "barcode", doc.barcode, update_modified=False)


def _backfill_reservation_types() -> None:
    if not frappe.db.table_exists("tabPlanned Material"):
        return
    rows = frappe.get_all(
        "Planned Material",
        filters={"reservation_entry": ("is", "set"), "reservation_entry_type": ("is", "not set")},
        fields=["name"],
        limit=5000,
    )
    for row in rows:
        frappe.db.set_value(
            "Planned Material",
            row.name,
            {
                "reservation_entry_type": "Material Request",
            },
            update_modified=False,
        )
