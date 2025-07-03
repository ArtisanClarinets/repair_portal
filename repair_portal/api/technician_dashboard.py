# repair_portal/api/technician_dashboard.py
# Updated: 2025-07-02
# Version: 1.3
# Purpose: Fortune-500 grade backend API for the Technician Dashboard.

import frappe
from frappe import _
from frappe.utils import add_months, nowdate
from decimal import Decimal

@frappe.whitelist()
def get_technician_dashboard_counts():
    """
    Fetches all the necessary data for the technician dashboard.
    This includes KPIs, assigned repairs, open tasks, and recent activity.
    """
    technician = frappe.session.user

    data = {
        "kpis": get_technician_kpis(technician),
        "assigned_repairs": get_assigned_repairs(technician),
        "open_tasks": get_open_tasks(technician),
        "recent_activity": get_recent_activity(technician),
    }

    return data

def get_technician_kpis(technician):
    """
    Calculates Key Performance Indicators for the given technician.
    """
    completed_this_month = frappe.db.count(
        "Repair Order",
        {
            "technician_assigned": technician,
            "status": "Closed",
            "modified": (">=", add_months(nowdate(), -1)),
        },
    )

    avg_days_raw = frappe.db.get_value(
        "Repair Order",
        {"technician_assigned": technician, "status": "Closed"},
        "avg(DATEDIFF(modified, creation))",
    )
    
    # Explicitly handle None and ensure the value is a number before rounding.
    avg_days_val = float(avg_days_raw) if avg_days_raw is not None else 0.0

    pending_qa = frappe.db.count(
        "Inspection Report", {"owner": technician, "status": "Pending Review"}
    )

    kpis = {
        "completed_repairs_this_month": completed_this_month,
        "avg_completion_time_days": round(avg_days_val, 2),
        "pending_qa_inspections": pending_qa,
    }
    return kpis

def get_assigned_repairs(technician):
    """
    Retrieves all repair orders assigned to the technician that are currently in progress.
    """
    return frappe.get_all(
        "Repair Order",
        fields=[
            "name",
            "instrument",
            "status",
            "estimated_completion",
            "total_cost",
        ],
        filters={"technician_assigned": technician, "status": "In Progress"},
        order_by="estimated_completion asc",
        limit=10,
    )

def get_open_tasks(technician):
    """
    Fetches all open repair tasks assigned to the technician.
    """
    return frappe.get_all(
        "Repair Task",
        fields=["name", "task_type", "description", "status", "est_hours"],
        filters={"assigned_to": technician, "status": "Pending"},
        order_by="creation asc",
        limit=10,
    )

def get_recent_activity(technician):
    """
    Gathers the most recent activities performed by the technician.
    """
    return frappe.get_all(
        "Activity Log",
        fields=["subject", "timeline_doctype", "timeline_name"],
        filters={"owner": technician},
        order_by="modified desc",
        limit=5,
    )