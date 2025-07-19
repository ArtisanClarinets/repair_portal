# File: repair_portal/repair_portal/lab/page/intonation_recorder/intonation_recorder.py
# Date Updated: 2025-06-29
# Version: 1.0
# Purpose: Technician-only Desk page for recording clarinet intonation audio

import frappe
from frappe import _


def get_context(context):
    """Renders the microphone recorder page inside Desk."""
    if not frappe.has_role("Technician"):
        frappe.throw(_("Only Technicians can access this page."), frappe.PermissionError)
