# File: repair_portal/www/repair_status.py
# Updated: 2025-06-16
# Version: 1.0
# Purpose: Public tracker for Clarinet Repair Log status and notes

import frappe


@frappe.whitelist(allow_guest=True)
def get_context(context):
    name = frappe.form_dict.get("name")
    if not name:
        frappe.throw("Missing tracker ID")

    doc = frappe.get_doc("Service Order Tracker", name)
    context.stage = doc.current_stage
    context.message = doc.message_to_customer
    context.history = doc.history_log
    return context