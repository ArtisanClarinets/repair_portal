"""
File: repair_portal/www/my_instruments.py
Updated: 2025-07-03
Version: 1.1
Purpose: Provides context for `/my_instruments` route with secure pagination handling.
"""

import frappe
from frappe import _

login_required = True

def get_context(context):
    user = frappe.session.user
    client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")
    filters = {"client_profile": client} if client else {"owner": user}

    # Clamp pagination values to avoid negatives or abuse
    try:
        limit_start = max(int(frappe.form_dict.get("start", 0)), 0)
    except Exception:
        limit_start = 0
    try:
        limit_page_length = max(int(frappe.form_dict.get("page_length", 20)), 1)
    except Exception:
        limit_page_length = 20

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
    return context
