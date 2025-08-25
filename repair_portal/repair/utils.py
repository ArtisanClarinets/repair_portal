# =============================================================================
# File Header
# Relative Path: repair_portal/repair/utils.py
# Date: 2025-08-25
# Version: v2.0.0
# Description:
# Cross-cutting utilities for the Repair Portal (Frappe v15).
# • Enforces customer/instrument consistency between child documents and their Repair Order.
# • Auto-appends child documents to the parent Repair Order’s related_documents table (idempotent).
# • Provides a meta-driven, idempotent mapper to create a Repair Order from a Repair Quotation.
# • Defensive by design: graceful no-ops when fields are missing; clear errors for missing targets.
# =============================================================================
# Generic utilities to (a) enforce consistency with Repair Order
# and (b) auto-append child docs into Repair Order.related_documents.

from __future__ import annotations
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

# =============================================================================
# Logic & Function (Documentation)
# Date: 2025-08-25
# Version: v1.1.0
# Scope:
# This section documents the original utilities that (a) keep child documents in
# sync with their parent Repair Order and (b) auto-link those children to the
# parent’s "related_documents" child table without creating duplicates.
# Key Components:
# • DOC_CONFIG (dict)
# - Maps each supported child DocType to the fieldnames that carry its
# Customer and Instrument references. Example:
# "Clarinet Intake": {"customer": "customer", "instrument": "instrument_profile"}
# - Extensible: add new doctypes or adjust fieldnames without changing code paths.
# • on_child_validate(doc, method=None)
# - Intended as a Doc Event handler (e.g., validate/on_update) on the listed child doctypes.
# - Early-returns if the child does not have a "repair_order" field (first-run safety) or if it is empty.
# - Loads the parent Repair Order (throws if missing/invalid), then:
# 1) Consistency checks:
# • If both parent and child expose "customer" fields and differ → frappe.throw with a clear message.
# • If both expose instrument fields (e.g., instrument_profile) and differ → frappe.throw.
# 2) Relationship maintenance:
# • Ensures the (doctype, name) pair exists in parent.related_documents, adding it only if absent.
# • Saves the parent with ignore_permissions=True to avoid permission friction in system workflows.
# • _ensure_related(parent, doctype, name, desc="")
# - Idempotently appends a row to parent.related_documents only if not already present.
# - Comparison is O(n) across the existing rows (n = len(related_documents)), which is typically small.
# Failure Modes & Guarantees:
# • If "repair_order" is provided but the parent cannot be fetched → the event will raise and block save.
# • If Customer/Instrument mismatch is detected → explicit frappe.throw with the parent’s name.
# • If DOC_CONFIG has no entry for the child doctype → consistency checks are skipped safely; relation still added.
# Security & Permissions:
# • Parent save uses ignore_permissions=True because this runs inside child doc flows; ensures linkage persists.
# If you require strict permission enforcement, remove ignore_permissions=True and ensure roles allow writes.
# Configuration Notes:
# • Wire this function in hooks.py for each relevant child doctype:
# doc_events = {
# "Clarinet Intake": {"validate": "repair_portal.repair.utils.on_child_validate"},
# "Instrument Inspection": {"validate": "repair_portal.repair.utils.on_child_validate"},
# ...
# }
# • To introduce a new child doctype, add its fieldnames to DOC_CONFIG.
# =============================================================================
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

# =============================================================================

# =============================================================================
# Added Mapping Utilities & Quotation→Order Creation – Logic & Function
# Date: 2025-08-25
# Version: v2.0.1
# Purpose:
#   Robust, meta-driven, idempotent creation of a "Repair Order" from a
#   "Repair Quotation", including defensive parent and child-row mapping.
# =============================================================================

__all__ = [
    "MappingError",
    "create_repair_order_from_quotation",
    "_find_child_table_and_doctype",
    "_child_map_fields",
    "_first_present_field",
    "_set_if_present",
]


class MappingError(frappe.ValidationError):
    """Explicit error type for mapping failures (missing targets, no child table, etc.)."""
    pass


def _first_present_field(meta, candidates: list[str]) -> str | None:
    """Return the first fieldname from candidates that exists on the given meta."""
    for name in candidates:
        if meta.has_field(name):
            return name
    return None


def _set_if_present(doc: Document, fieldname: str, value):
    """
    Set a field only if:
      • value is not None/empty, and
      • target Doc has that field in its meta.
    """
    if value is None or value == "":
        return
    if doc.meta.has_field(fieldname):
        doc.set(fieldname, value)


def _find_child_table_and_doctype(order_meta) -> tuple[str, str]:
    """
    Identify the most likely child table on Repair Order.
    Preference order:
      1) Known fieldnames
      2) Known child-doctype names
      3) First Table field available
    """
    preferred_fieldnames = ["items", "services", "repair_items", "repairs", "operations", "tasks"]
    preferred_child_dts = ["Repair Order Item", "Repair Service Item", "Repair Items", "Repair Task"]

    # 1) Exact fieldname preference
    for f in order_meta.fields:
        if f.fieldtype == "Table" and f.fieldname in preferred_fieldnames and f.options:
            return f.fieldname, f.options

    # 2) By options (child doctype name)
    for f in order_meta.fields:
        if f.fieldtype == "Table" and f.options in preferred_child_dts:
            return f.fieldname, f.options

    # 3) Fallback: first table we see
    for f in order_meta.fields:
        if f.fieldtype == "Table" and f.options:
            return f.fieldname, f.options

    raise MappingError("No child Table field found on 'Repair Order' to receive items.")


def _child_map_fields(child_meta, src_row) -> dict:
    """
    Transform a Repair Quotation Item row into a Repair Order child-row dict
    using flexible, meta-driven fieldname picking.
    """
    def pick(cands, default=None):
        name = _first_present_field(child_meta, cands)
        return name if name else default

    row: dict = {}

    map_pairs = [
        (["item_type", "type", "service_type"], src_row.get("item_type")),
        (["item_code", "code", "item"], src_row.get("item_code")),
        (["description", "item_name", "remarks", "note"], src_row.get("description")),
        (["qty", "quantity", "hours_qty"], src_row.get("qty")),
        (["uom", "unit"], src_row.get("uom")),
        (["hours", "labor_hours"], src_row.get("hours")),
        (["rate", "price", "unit_price"], src_row.get("rate")),
        (["amount", "total", "line_total"], src_row.get("amount")),
        (["technician", "assigned_to", "employee"], src_row.get("technician")),
        (["notes", "line_notes"], src_row.get("notes")),
    ]

    for candidates, value in map_pairs:
        fieldname = pick(candidates)
        if fieldname and value not in (None, ""):
            row[fieldname] = value

    return row


def create_repair_order_from_quotation(quotation: str | Document, submit: bool = False) -> Document:
    """
    Create a Repair Order from a Repair Quotation (idempotent).
    Steps:
      1) Load source quotation (by name or object).
      2) If already linked via `repair_order`, return that order.
      3) Ensure target doctype 'Repair Order' exists.
      4) new_doc('Repair Order'); meta-driven parent field mapping.
      5) Detect child table; map & append rows.
      6) Insert; optionally submit.
      7) Link back to quotation via `repair_order` (if field exists).

    Returns:
      A saved (and possibly submitted) Repair Order Document.
    """
    # 1) Load source quotation
    qdoc = frappe.get_doc("Repair Quotation", quotation) if isinstance(quotation, str) else quotation

    # 2) Idempotency: reuse linked order if present
    if getattr(qdoc, "repair_order", None):
        return frappe.get_doc("Repair Order", qdoc.repair_order)  # type: ignore

    # 3) Ensure target doctype exists
    try:
        order_meta = frappe.get_meta("Repair Order")
    except frappe.DoesNotExistError:
        raise MappingError("Target DocType 'Repair Order' does not exist. Please create it first.")

    # 4) Create target document
    order = frappe.new_doc("Repair Order")

    # Parent field mapping (defensive)
    _set_if_present(order, "customer", getattr(qdoc, "customer", None))
    _set_if_present(order, "company", getattr(qdoc, "company", None))
    _set_if_present(order, "currency", getattr(qdoc, "currency", None))

    # Instrument context (clarinet specifics)
    _set_if_present(order, "instrument_type", getattr(qdoc, "instrument_type", None))
    _set_if_present(order, "brand", getattr(qdoc, "brand", None))
    _set_if_present(order, "model", getattr(qdoc, "model", None))
    _set_if_present(order, "serial_no", getattr(qdoc, "serial_no", None))
    _set_if_present(order, "bore_diameter_mm", getattr(qdoc, "bore_diameter_mm", None))
    _set_if_present(order, "condition_notes", getattr(qdoc, "condition_notes", None))
    _set_if_present(order, "setup_notes", getattr(qdoc, "setup_notes", None))

    # Back-references (if the fields exist on target)
    _set_if_present(order, "repair_quotation", qdoc.name)
    _set_if_present(order, "quotation", qdoc.name)

    # Operational hints
    _set_if_present(order, "order_date", now_datetime())
    _set_if_present(order, "owner_signature", getattr(qdoc, "owner_signature", None))

    # 5) Child table mapping
    child_fieldname, child_dt = _find_child_table_and_doctype(order_meta)
    child_meta = frappe.get_meta(child_dt)

    for s in (getattr(qdoc, "items", None) or []):
        row_dict = _child_map_fields(child_meta, s.as_dict())
        order.append(child_fieldname, row_dict)

    # 6) Insert; optionally submit
    order.insert(ignore_permissions=False)

    if submit and getattr(order, "docstatus", 0) == 0 and order.meta.is_submittable:  # type: ignore
        order.submit()

    # 7) Link back to quotation to cement idempotency
    if qdoc.meta.has_field("repair_order"):
        qdoc.db_set("repair_order", order.name)

    return order
