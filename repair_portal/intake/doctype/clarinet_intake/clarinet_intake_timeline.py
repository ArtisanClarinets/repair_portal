# File: repair_portal/intake/doctype/clarinet_intake/clarinet_intake_timeline.py
# Last Updated: 2025-07-29
# Purpose: After Clarinet Intake is created, log each auto-generated child record in the timeline

from __future__ import annotations
import frappe
from frappe.utils import get_url_to_form
from frappe.model.document import Document

def add_timeline_entries(doc: Document, method: str) -> None:
    """
    Called via `after_insert` on Clarinet Intake.
    For each of the child records potentially created by the main controller,
    add an 'Info' comment with a link.
    """
    # helper to log one entry
    def log(doctype: str, name: str, label: str):
        if not name:
            return
        url = get_url_to_form(doctype, name)
        doc.add_comment(
            comment_type="Info",
            text=f"🔹 {label} <b><a href=\"{url}\" style=\"text-decoration: none;\">{name}</a></b> created."
        )

    # 1) Item (only for New Inventory)
    if getattr(doc, "intake_type", None) == "New Inventory" and doc.item_code:
        item = frappe.db.get_value("Item", {"item_code": doc.item_code})
        log("Item", item, "Item")

    # 2) Serial No
    if doc.serial_no:
        serial = frappe.db.get_value("Serial No", {"serial_no": doc.serial_no})
        log("Serial No", serial, "Serial No")

    # 3) Instrument
    if getattr(doc, "instrument", None):
        log("Instrument", doc.instrument, "Instrument")

    # 4) Instrument Inspection
    insp = frappe.db.get_value(
        "Instrument Inspection",
        {"intake_record_id": doc.name}
    )
    log("Instrument Inspection", insp, "Instrument Inspection")

    # 5) Clarinet Initial Setup (only for New Inventory)
    if getattr(doc, "intake_type", None) == "New Inventory":
        setup = frappe.db.get_value(
            "Clarinet Initial Setup",
            {"intake": doc.name}
        )
        log("Clarinet Initial Setup", setup, "Clarinet Initial Setup")