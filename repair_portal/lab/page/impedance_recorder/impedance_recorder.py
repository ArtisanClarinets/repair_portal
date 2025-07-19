# File: repair_portal/lab/page/impedance_recorder/impedance_recorder.py
# Updated: 2025-06-29
# Version: 1.0
# Purpose: Desk page for recording impedance data via mic

import frappe
from frappe import _


def get_context(context):
    if not frappe.has_role("Technician"):
        frappe.throw(_("Only Technicians can access this page."), frappe.PermissionError)
