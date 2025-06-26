# Report: Repair Tasks by Type
# Module: Repair Logging
# Updated: 2025-06-12

import frappe


def execute(filters=None):
    columns = [
        {"fieldname": "task_type", "label": "Task Type", "fieldtype": "Data", "width": 200},
        {"fieldname": "task_count", "label": "Task Count", "fieldtype": "Int", "width": 120},
    ]

    data = frappe.db.sql(
        """
        SELECT task_type, COUNT(name) AS task_count
        FROM `tabRepair Task Log`
        GROUP BY task_type
    """,
        as_dict=True,
    )

    return columns, data
