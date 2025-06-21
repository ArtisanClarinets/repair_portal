# File: www/my_signatures/index.py
# Updated: 2025-06-20
# Purpose: Display signature archive table for technician or customer portal view

import frappe
from frappe import _
from frappe.utils import get_fullname

def get_context(context):
    user = frappe.session.user
    is_tech = frappe.has_role("Technician")

    filters = {}
    if not is_tech:
        filters["owner"] = user

    signoffs = frappe.get_all(
        "Customer Sign Off",
        filters=filters,
        fields=[
            "name", "signed_at", "ip_address", "signature_hash", "reference_doctype", "reference_name"
        ],
        order_by="signed_at desc"
    )

    for s in signoffs:
        pdf = frappe.db.get_value("File", {"attached_to_doctype": "Customer Sign Off", "attached_to_name": s.name}, "file_url")
        s["pdf_url"] = pdf

    context.signoffs = signoffs
    context.title = _("Signature Archive")
    return context