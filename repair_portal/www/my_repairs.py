"""Web controller: show repairs for logged in user."""
# File: repair_portal/www/my_repairs.py
# Updated: 2024-06-19
# Version: 1.0
# Purpose: Provides context for `/my_repairs` route.

import frappe
from frappe import _

login_required = True


def get_context(context):
    user = frappe.session.user
    client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")
    filters = {"owner": user}
    if client:
        filters = {"owner": frappe.db.get_value("Client Profile", client, "linked_user") or user}

    limit_start = int(frappe.form_dict.get("start", 0))
    limit_page_length = int(frappe.form_dict.get("page_length", 20))

    context.title = _("My Repairs")
    context.repair_requests = frappe.get_all(
        "Repair Request",
        fields=["name", "status", "date_reported", "instrument_category"],
        filters=filters,
        order_by="creation desc",
        limit_start=limit_start,
        limit_page_length=limit_page_length,
    )
    context.inspections = frappe.get_all(
        "Inspection Report",
        fields=["name", "inspection_date", "instrument_id"],
        filters=filters,
        order_by="creation desc",
        limit_start=limit_start,
        limit_page_length=limit_page_length,
    )
    return context
