# Generic utilities to (a) enforce consistency with Repair Order
# and (b) auto-append child docs into Repair Order.related_documents.

from __future__ import annotations
import frappe
from frappe import _

# Map child doctypes to the fieldnames used for customer and instrument
DOC_CONFIG = {
    "Clarinet Intake": {"customer": "customer", "instrument": "instrument_profile"},
    "Instrument Inspection": {"customer": "customer", "instrument": "instrument_profile"},
    "Service Plan": {"customer": "customer", "instrument": "instrument_profile"},
    "Repair Estimate": {"customer": "customer", "instrument": "instrument_profile"},
    "Final QA Checklist": {"customer": "customer", "instrument": "instrument_profile"},
    "Measurement Session": {"customer": "customer", "instrument": "instrument_profile"},
    "Diagnostic Metrics": {"customer": "customer", "instrument": "instrument_profile"},
    "Repair Task": {"customer": "customer", "instrument": "instrument_profile"},
}

def on_child_validate(doc, method=None):
    """Doc event handler for children: validate link & consistency and
    ensure presence under parent.related_documents."""
    # 1) If the Custom Field is not present, do nothing (first run safety)
    if not hasattr(doc, "repair_order"):
        return

    if not doc.repair_order:
        return

    # 2) Ensure parent exists
    parent = frappe.get_doc("Repair Order", doc.repair_order)

    # 3) Enforce customer/instrument consistency when fields exist on both
    cfg = DOC_CONFIG.get(doc.doctype, {})
    child_customer = getattr(doc, cfg.get("customer", ""), None)
    child_instrument = getattr(doc, cfg.get("instrument", ""), None)

    if parent.customer and child_customer and parent.customer != child_customer: # type: ignore
        frappe.throw(_("Customer mismatch with Repair Order {0}.").format(parent.name))

    if parent.instrument_profile and child_instrument and parent.instrument_profile != child_instrument: # type: ignore
        frappe.throw(_("Instrument mismatch with Repair Order {0}.").format(parent.name))

    # 4) Append to parent.related_documents if missing
    _ensure_related(parent, doc.doctype, doc.name, desc="Auto-linked")
    parent.save(ignore_permissions=True)

def _ensure_related(parent, doctype, name, desc=""):
    exists = any(
        (row.doctype_name == doctype and row.document_name == name)
        for row in (parent.related_documents or [])
    )
    if not exists:
        parent.append("related_documents", {
            "doctype_name": doctype,
            "document_name": name,
            "description": desc,
        })
