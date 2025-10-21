# File: repair_portal/intake/doctype/clarinet_intake/clarinet_intake_timeline.py
# Last Updated: 2025-08-14
# Purpose: After Clarinet Intake is created, log each auto-generated child record in the timeline.
#          Updated to prefer Instrument Serial Number (ISN) over ERPNext Serial No, with legacy fallback.

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import get_url_to_form

# ISN resolver (raw → ISN)
try:
    from repair_portal.utils.serials import find_by_serial as isn_find_by_serial  # type: ignore
except Exception:

    def isn_find_by_serial(serial_input: str):
        return None


def add_timeline_entries(doc: Document, method: str) -> None:
    """
    Called via `after_insert` on Clarinet Intake.
    For each of the child records potentially created by the main controller,
    add an 'Info' comment with a link.
    """

    # helper to log one entry
    def log(doctype: str, name: str | None, label: str):
        if not name:
            return
        url = get_url_to_form(doctype, name)
        doc.add_comment(
            comment_type="Info",
            text=f'🔹 {label} <b><a href="{url}" style="text-decoration: none;">{name}</a></b> created.',
        )

    # 1) Item (only for New Inventory)
    if getattr(doc, "intake_type", None) == "New Inventory" and doc.item_code:  # type: ignore
        item = frappe.db.get_value("Item", {"item_code": doc.item_code})  # type: ignore
        log("Item", item, "Item")  # type: ignore

    # 2) Instrument Serial Number (preferred) or ERPNext Serial No (legacy fallback)
    if doc.serial_no:  # type: ignore
        isn = isn_find_by_serial(doc.serial_no)  # type: ignore
        if isn and isn.get("name"):
            log("Instrument Serial Number", isn["name"], "Instrument Serial Number")
        else:
            # Legacy ERPNext Serial No might still exist
            serial = frappe.db.get_value("Serial No", {"serial_no": doc.serial_no})  # type: ignore
            log("Serial No", serial, "Serial No")  # type: ignore

    # 3) Instrument
    if getattr(doc, "instrument", None):
        log("Instrument", doc.instrument, "Instrument")  # type: ignore

    # 4) Instrument Inspection
    insp = frappe.db.get_value("Instrument Inspection", {"intake_record_id": doc.name})
    log("Instrument Inspection", insp, "Instrument Inspection")  # type: ignore

    # 5) Clarinet Initial Setup (only for New Inventory)
    if getattr(doc, "intake_type", None) == "New Inventory":
        setup = frappe.db.get_value("Clarinet Initial Setup", {"intake": doc.name})
        log("Clarinet Initial Setup", setup, "Clarinet Initial Setup")  # type: ignore
