# File: repair_portal/instrument_profile/page/instrument_history/instrument_history.py
# Created: 2025-06-13
# Version: 1.0
# Purpose: Custom page to show a unified view of an instrument's profile, setup logs, inspections.

import frappe
from frappe import _
from frappe.utils.jinja import render_template
from frappe.www.page_renderer import render_page

@frappe.whitelist()
def get_instrument_history(instrument_id):
    doc = frappe.get_doc("Instrument Profile", instrument_id)
    setups = frappe.get_all("Clarinet Initial Setup", fields=["name", "setup_date", "technician", "status"], filters={"instrument_profile": instrument_id})
    conditions = frappe.get_all("Instrument Condition Record", fields=["date", "technician", "condition_notes"], filters={"parent": instrument_id})
    return {
        "doc": doc,
        "setups": setups,
        "conditions": conditions
    }