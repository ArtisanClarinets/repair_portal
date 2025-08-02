# File: repair_portal/lab/page/tone_fitness_recorder/tone_fitness_recorder.py
# Updated: 2025-06-29
# Purpose: Desk page for tone fitness measurement
import frappe
from frappe import _


def get_context(context):
    if not frappe.has_role("Technician"): # type: ignore
        frappe.throw(_("Only Technicians can access this page."), frappe.PermissionError)
