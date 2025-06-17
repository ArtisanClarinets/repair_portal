# File: repair_portal/www/repair_request.py
# Updated: 2025-06-16
# Version: 1.0
# Purpose: Controller for customer portal Repair Request detailed view

import frappe
from frappe import _
from frappe.utils import get_fullname


def get_context(context):
    request_id = frappe.form_dict.name
    doc = frappe.get_doc("Repair Request", request_id)

    if doc.customer != frappe.session.user:
        frappe.throw(_("Not permitted"))

    context.doc = doc
    context.fullname = get_fullname(frappe.session.user)
    return context