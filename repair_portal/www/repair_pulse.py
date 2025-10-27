"""Web controller: real-time repair pulse updates."""

# File: repair_portal/www/repair_pulse.py
# Updated: 2024-06-19
# Version: 1.0
# Purpose: Provides context for `/repair_pulse` route.

import frappe
from frappe import _

from repair_portal.customer.security import ensure_customer_access

login_required = True


def get_context(context):
    frappe.only_for(("Client", "Technician"))  # type: ignore
    name = frappe.form_dict.get("name")
    if not name:
        frappe.throw(_("Repair Request not specified"))

    doc = frappe.get_doc("Repair Request", name)  # type: ignore
    user = frappe.session.user
    if "Technician" not in frappe.get_roles(user):
        ensure_customer_access(getattr(doc, "customer", None), user)

    updates = frappe.get_all(
        "Pulse Update",
        fields=["name", "update_time", "status", "details", "percent_complete"],
        filters={"repair_request": name},
        order_by="update_time asc",
    )

    context.repair_request = doc
    context.updates = updates
    context.updates_json = frappe.safe_json.dumps(updates)  # type: ignore
    context.channel = f"repair_pulse_{name}"
    return context
