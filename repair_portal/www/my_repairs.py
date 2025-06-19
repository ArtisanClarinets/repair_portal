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
    context.repairs = frappe.get_all(
        "Repair Request",
        fields=[
            "name",
            "status",
            "date_reported as date",
            "issue_description as description",
            "instrument_category as instrument",
        ],
        filters=filters,
        order_by="creation desc",
        limit_start=limit_start,
        limit_page_length=limit_page_length,
    )
    context.repairs_json = frappe.safe_json.dumps(context.repairs)
    context.empty_message = _("No repairs found.")
    return context
