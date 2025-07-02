"""
File: repair_portal/api/dashboard.py
Date Updated: 2025-07-02
Version: 1.0
Purpose: Backend APIs to provide counts and recent activity for the Technician Dashboard.
"""

import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def get_technician_dashboard_counts():
    counts = {}

    counts["repair_orders_open"] = frappe.db.count("Repair Order", {"status": ["in", ["Open", "In Progress"]]})
    counts["repair_orders_closed"] = frappe.db.count("Repair Order", {"status": "Closed"})

    counts["repair_tasks_due_today"] = frappe.db.count("Repair Task", {
        "status": "Open",
        "expected_completion_date": now_datetime().date()
    })

    counts["intake_jobs_open"] = frappe.db.count("Clarinet Intake", {"workflow_state": ["not in", ["Closed", "Cancelled"]]})

    counts["qa_pending"] = frappe.db.count("Final QA Checklist", {"workflow_state": "Pending"})

    counts["loaners_out"] = frappe.db.count("Loaner Instrument", {"status": "Checked Out"})

    counts["instruments_in_service"] = frappe.db.count("Instrument Profile", {"status": "In Service"})

    return counts


@frappe.whitelist()
def get_recent_activity():
    activity = {}

    activity["repair_orders"] = frappe.get_all("Repair Order", fields=["name", "status", "modified"], order_by="modified desc", limit=10)
    activity["repair_tasks"] = frappe.get_all("Repair Task", fields=["name", "status", "expected_completion_date", "modified"], order_by="modified desc", limit=10)
    activity["intakes"] = frappe.get_all("Clarinet Intake", fields=["name", "workflow_state", "modified"], order_by="modified desc", limit=10)
    activity["qa"] = frappe.get_all("Final QA Checklist", fields=["name", "workflow_state", "modified"], order_by="modified desc", limit=10)

    return activity