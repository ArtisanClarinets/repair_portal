# File: repair_portal/repair_portal/report/technician_task_summary/technician_task_summary.py
# Updated: 2025-06-16
# Version: 1.0
# Purpose: Script Report to summarize Repair Request counts by status for assigned technician

import frappe


def execute(filters=None):
    technician = filters.get('technician') if filters else frappe.session.user

    data = frappe.db.sql(
        """
        SELECT
            status,
            COUNT(*) AS total
        FROM `tabRepair Request`
        WHERE technician_assigned = %s
        GROUP BY status
    """,
        (technician,),
        as_dict=True,
    )

    columns = [
        {'label': 'Status', 'fieldname': 'status', 'fieldtype': 'Data', 'width': 150},
        {'label': 'Total', 'fieldname': 'total', 'fieldtype': 'Int', 'width': 100},
    ]

    return columns, data
