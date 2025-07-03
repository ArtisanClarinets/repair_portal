"""
File: repair_portal/www/instrument_profile.py
Updated: 2025-07-03
Version: 1.1
Purpose: Dynamic instrument profile page for logged-in user. Enforces login requirement.
"""

import frappe

login_required = True

def get_context(context):
    user = frappe.session.user
    instrument_name = frappe.form_dict.get("name")
    if not instrument_name:
        frappe.throw("Missing instrument identifier")

    # Verify user owns the instrument or is linked
    client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")
    instrument = frappe.get_doc("Instrument Profile", instrument_name)
    if instrument.client_profile != client and instrument.owner != user:
        frappe.throw("You are not authorized to view this instrument.")

    context.instrument = instrument
    context.title = f"{instrument.instrument_name} ({instrument.serial_number})"
    return context
