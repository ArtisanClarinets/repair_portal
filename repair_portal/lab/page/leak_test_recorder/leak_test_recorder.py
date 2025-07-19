# File: repair_portal/lab/page/leak_test_recorder/leak_test_recorder.py
# Updated: 2025-06-29
# Purpose: Desk page for capturing leak decay via mic
import frappe
from frappe import _


def get_context(context):
    if not frappe.has_role("Technician"):
        frappe.throw(_("Only Technicians can access this page."), frappe.PermissionError)
