# Report: Repair Bay Utilization
# Module: Service Planning
# Updated: 2025-06-12

import frappe


def execute(filters=None):
    columns = [
        {"fieldname": "bay", "label": "Repair Bay", "fieldtype": "Data", "width": 160},
        {"fieldname": "task_count", "label": "Tasks Scheduled", "fieldtype": "Int", "width": 160},
    ]

    data = frappe.db.sql(
        """
        SELECT bay as bay, COUNT(name) as task_count
        FROM `tabService Task`
        WHERE bay IS NOT NULL
        GROUP BY bay
    """,
        as_dict=True,
    )

    return columns, data
