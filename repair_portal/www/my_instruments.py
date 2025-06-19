"""Web controller: list instruments owned by the logged in user."""

# File: repair_portal/www/my_instruments.py
# Updated: 2024-06-19
# Version: 1.0
# Purpose: Provides context for `/my_instruments` route.

import frappe
from frappe import _

login_required = True


def get_context(context):
    user = frappe.session.user
    client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")
    filters = {"client_profile": client} if client else {"owner": user}

    limit_start = int(frappe.form_dict.get("start", 0))
    limit_page_length = int(frappe.form_dict.get("page_length", 20))

    context.title = _("My Instruments")
    context.introduction = _("Your Instrument Portfolio")
    context.instruments = frappe.get_all(
        "Instrument Profile",
        fields=[
            "name",
            "instrument_name",
            "serial_number",
            "brand",
            "model",
            "status",
            "route",
        ],
        filters=filters,
        limit_start=limit_start,
        limit_page_length=limit_page_length,
    )
    context.instruments_json = frappe.safe_json.dumps(context.instruments)
    context.empty_message = _("No instruments found.")
    return context
