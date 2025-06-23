"""Public tracker for the service order status."""

import frappe


def get_context(context):
    """Return status information for a repair tracker."""
    name = frappe.form_dict.get("name")
    if not name:
        frappe.throw("Missing tracker ID")

    doc = frappe.get_doc("Service Order Tracker", name)
    context.stage = doc.current_stage
    context.message = doc.message_to_customer
    context.history = doc.history_log
    context.title = f"Repair Status for {doc.instrument_name}"
    return context
