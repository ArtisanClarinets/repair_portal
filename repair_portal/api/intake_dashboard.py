# relative path: repair_portal/api/intake_dashboard.py
# date updated: 2025-07-02
# version: 1.0.0
# purpose: API endpoints for Intake Dashboard

import frappe


@frappe.whitelist(allow_guest=False)
def get_intake_counts():
    statuses = [
        'Pending',
        'Received',
        'Inspection',
        'Repair',
        'Awaiting Customer Approval',
        'Complete',
    ]
    return {
        status: frappe.db.count('Clarinet Intake', {'intake_status': status})
        for status in statuses
    }


@frappe.whitelist(allow_guest=False)
def get_recent_intakes():
    return frappe.get_all(
        'Clarinet Intake',
        fields=['name', 'intake_status', 'customer', 'instrument', 'modified'],
        order_by='modified desc',
        limit=10,
    )
