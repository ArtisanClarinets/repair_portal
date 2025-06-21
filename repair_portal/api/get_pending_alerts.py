# File: repair_portal/repair_portal/api/get_pending_alerts.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Return count of pending service tasks and expiring warranties for client dashboard alerts

import frappe
from frappe.utils import nowdate, add_days

@frappe.whitelist()
def get_pending_alerts():
    pending_tasks = frappe.db.count("Repair Order", {
        "docstatus": ["<", 2],
        "status": ["!=", "Closed"]
    })

    expiring_warranties = frappe.db.count("Warranty", {
        "warranty_expiry_date": ["<=", add_days(nowdate(), 30)]
    })

    return {
        "pending_tasks": pending_tasks,
        "expiring_warranties": expiring_warranties
    }