"""Web controller: technician job assignments list."""
# File: repair_portal/www/technician_dashboard.py
# Updated: 2024-06-19
# Version: 1.0
# Purpose: Provides context for `/technician_dashboard` route.

import frappe
from frappe import _

login_required = True


def get_context(context):
    user = frappe.session.user
    limit_start = int(frappe.form_dict.get("start", 0))
    limit_page_length = int(frappe.form_dict.get("page_length", 20))

    context.title = _("Technician Dashboard")
    context.assignments = frappe.get_all(
        "Repair Request",
        fields=["name", "status", "priority_level", "date_reported"],
        filters={"technician_assigned": user},
        order_by="priority_level desc, date_reported asc",
        limit_start=limit_start,
        limit_page_length=limit_page_length,
    )
    return context
