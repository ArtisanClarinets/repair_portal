# Path: repair_portal/repair/report/technician_utilization/technician_utilization.py
# Date: 2025-11-30
# Version: 1.1.0
# Purpose: Calculates total hours per technician from Repair Tasks (with SQL injection fix)
# Dependencies: frappe

import frappe
from frappe.utils import getdate


def execute(filters=None):
    filters = filters or {}
    conditions = []
    params = {}
    
    # Use parameterized queries to prevent SQL injection
    if filters.get("from_date"):
        # Validate and sanitize date input
        try:
            from_date = getdate(filters["from_date"])
            conditions.append("creation >= %(from_date)s")
            params["from_date"] = from_date
        except Exception:
            frappe.throw("Invalid from_date format")
    
    if filters.get("to_date"):
        # Validate and sanitize date input
        try:
            to_date = getdate(filters["to_date"])
            conditions.append("creation <= %(to_date)s")
            params["to_date"] = to_date
        except Exception:
            frappe.throw("Invalid to_date format")

    where_clause = f'WHERE {" AND ".join(conditions)}' if conditions else ""

    data = frappe.db.sql(
        f"""
        SELECT
            technician,
            SUM(actual_hours) AS total_hours,
            COUNT(name) AS task_count
        FROM `tabRepair Task`
        {where_clause}
        GROUP BY technician
    """,
        params,
        as_dict=True,
    )

    columns = [
        {"label": "Technician", "fieldname": "technician", "fieldtype": "Link", "options": "User"},
        {"label": "Total Hours", "fieldname": "total_hours", "fieldtype": "Float"},
        {"label": "Tasks Completed", "fieldname": "task_count", "fieldtype": "Int"},
    ]

    return columns, data
