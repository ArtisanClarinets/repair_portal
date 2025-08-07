# relative path: repair_portal/api/intake_dashboard.py
# date updated: 2025-07-02
# version: 1.0.0
# purpose: API endpoints for Intake Dashboard

import frappe


@frappe.whitelist(allow_guest=False)
def get_intake_counts():
    return {
        "New": frappe.db.count("Clarinet Intake", {"workflow_state": "New"}),
        "Received": frappe.db.count("Clarinet Intake", {"workflow_state": "Received"}),
        "Inspection": frappe.db.count("Clarinet Intake", {"workflow_state": "Inspection"}),
        "QC": frappe.db.count("Clarinet Intake", {"workflow_state": "QC"}),
        "Hold": frappe.db.count("Clarinet Intake", {"workflow_state": "Hold"}),
    }


@frappe.whitelist(allow_guest=False)
def get_recent_intakes():
    return frappe.get_all(
        "Clarinet Intake",
        fields=["name", "workflow_state", "client", "player", "modified"],
        order_by="modified desc",
        limit=10,
    )
