# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake_serial.py
# Last Updated: 2025-07-19
# Version: v1.2
# Purpose: Auto-create **Serial No** records *and* ensure the Clarinet Intake
#          links to (or auto-creates) an Instrument doc by serial number and item.
# Dependencies: frappe (>=15), ERPNext Stock module enabled

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

# ---------------------------------------------------------------------------
# PUBLIC API (wired via hooks.doc_events)
# ---------------------------------------------------------------------------

def create_serial_no(doc: "frappe.model.document.Document", method: str | None = None) -> None:  # noqa: D401
    """Event hook: run on *after_insert* and *on_submit* of Clarinet Intake.

    1. Create *Serial No* if it doesn’t yet exist.
    2. Link—or auto-create—an *Instrument* document so analytics always have
       a canonical Instrument record keyed by serial number and item.
    """
    if not doc.serial_no:
        return  # nothing to do
    _ensure_serial_no(doc)
    _ensure_instrument(doc)

# ---------------------------------------------------------------------------
# SERIAL NO LOGIC
# ---------------------------------------------------------------------------

def _ensure_serial_no(doc: "frappe.model.document.Document") -> None:
    # Prefer user-provided Item Code if present, else deduce
    item_code = getattr(doc, "item_code", None) or _deduce_item_code(doc)
    if frappe.db.exists("Serial No", doc.serial_no):
        return  # Already present
    sn = frappe.new_doc("Serial No")
    sn.serial_no = doc.serial_no
    sn.item_code = item_code
    sn.status = "Active"
    sn.purchase_document_type = "Clarinet Intake"
    sn.purchase_document_no = doc.name
    if getattr(doc, "warranty_months", None):
        sn.warranty_period = doc.warranty_months
    sn.warehouse = _default_inventory_warehouse()
    try:
        sn.insert(ignore_permissions=True)
        frappe.msgprint(_(f"Serial No <b>{sn.name}</b> created."))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _(f"Serial No creation failed for {doc.serial_no}"))
        frappe.throw(_(f"Failed to create Serial No: {e}"))

# ---------------------------------------------------------------------------
# INSTRUMENT LOGIC
# ---------------------------------------------------------------------------

def _ensure_instrument(doc: "frappe.model.document.Document") -> None:
    """Link Intake ⇄ Instrument; create Instrument if it doesn’t exist, and link Item if available."""
    if doc.get("instrument_unique_id"):
        return  # Already linked
    inst_name = frappe.db.get_value("Instrument", {"serial_no": doc.serial_no}, "name")
    if not inst_name:
        inst = frappe.new_doc("Instrument")
        inst.serial_no = doc.serial_no
        inst.manufacturer = doc.get("manufacturer")
        inst.model = doc.get("model")
        inst.clarinet_type = doc.get("clarinet_type")
        inst.body_material = doc.get("body_material")
        inst.keywork_plating = doc.get("keywork_plating")
        inst.pitch_standard = doc.get("pitch_standard")
        inst.year_of_manufacture = doc.get("year_of_manufacture")
        # Link to Item if available
        item_code = getattr(doc, "item_code", None)
        if item_code and frappe.db.exists("Item", {"item_code": item_code}):
            inst.item_code = item_code
        inst.insert(ignore_permissions=True)
        inst_name = inst.name
        frappe.msgprint(_(f"Instrument <b>{inst_name}</b> created and linked."))
    doc.db_set("instrument_unique_id", inst_name, update_modified=False)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _deduce_item_code(doc: "frappe.model.document.Document") -> str:
    """Map clarinet type to Item Code; fall back to generic."""
    mapping = {
        "B♭ Soprano": "CLARINET-BB",
        "A Soprano": "CLARINET-A",
        "E♭ Soprano": "CLARINET-EB",
        "B♭ Bass": "CLARINET-BASS",
    }
    return mapping.get(getattr(doc, "clarinet_type", None), "CLARINET")

def _default_inventory_warehouse() -> str | None:
    return frappe.db.get_single_value("Stock Settings", "inventory_warehouse")
