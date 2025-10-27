from __future__ import annotations

from typing import Optional

import frappe
from frappe import _


no_cache = 1


def get_context(context: dict) -> dict:
    if frappe.session.user == "Guest":
        frappe.throw(_("Please sign in to use the scanning console."), frappe.PermissionError)
    context["show_sidebar"] = False
    return context


@frappe.whitelist()
def resolve_code(code: str) -> dict[str, str]:
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)
    code = (code or "").strip()
    if not code:
        frappe.throw(_("Please provide a code."))

    for doctype in ("Repair Order", "Clarinet Intake", "Instrument"):
        record = _lookup_barcode(doctype, code)
        if record:
            if not frappe.has_permission(doctype, "read", doc=record):
                frappe.throw(_("You do not have access to {0}").format(doctype), frappe.PermissionError)
            return {
                "doctype": doctype,
                "name": record.name,
                "route": frappe.utils.get_url_to_form(doctype, record.name),
            }

    frappe.throw(_("No matching record was found for {0}").format(frappe.bold(code)))


def _lookup_barcode(doctype: str, code: str) -> Optional[frappe.Document]:
    name = frappe.db.get_value(doctype, {"barcode": code}, "name")
    if not name:
        return None
    return frappe.get_doc(doctype, name)
