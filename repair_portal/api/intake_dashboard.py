# relative path: repair_portal/api/intake_dashboard.py
# date updated: 2025-07-02
# version: 1.0.0
# purpose: API endpoints for Intake Dashboard

import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def get_intake_counts():
    if not frappe.has_permission("Clarinet Intake", "read"):
        frappe.throw(_("Insufficient permissions to view intake dashboard."), frappe.PermissionError)

    statuses = [
        "Pending",
        "Received",
        "Inspection",
        "Repair",
        "Awaiting Customer Approval",
        "Complete",
    ]

    # Optimized to use single query instead of N+1
    counts = frappe.db.sql("""
        SELECT intake_status, count(*) as count
        FROM `tabClarinet Intake`
        WHERE intake_status IN %(statuses)s
        GROUP BY intake_status
    """, {"statuses": statuses}, as_dict=True)

    count_map = {row.intake_status: row.count for row in counts}

    return {status: count_map.get(status, 0) for status in statuses}


@frappe.whitelist(allow_guest=False)
def get_recent_intakes():
    if not frappe.has_permission("Clarinet Intake", "read"):
        frappe.throw(_("Insufficient permissions to view intake dashboard."), frappe.PermissionError)

    # Use get_list to enforce User Permissions (row-level security)
    return frappe.get_list(
        "Clarinet Intake",
        fields=["name", "intake_status", "customer", "instrument", "modified"],
        order_by="modified desc",
        limit=10,
    )
