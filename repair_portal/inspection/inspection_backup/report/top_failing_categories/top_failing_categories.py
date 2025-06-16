# File: repair_portal/repair_portal/inspection/report/top_failing_categories/top_failing_categories.py
# Updated: 2025-06-12
# Version: 1.0
# Purpose: Report frequency of failed checklist categories

import frappe


def execute(filters=None):
    data = frappe.db.sql(
        """
        SELECT item_description AS category,
               COUNT(*) AS fail_count
        FROM `tabInspection Checklist Item`
        WHERE `pass` = 0
        GROUP BY item_description
        ORDER BY fail_count DESC
        LIMIT 10
    """,
        as_dict=True,
    )

    columns = [
        {'label': 'Finding Type', 'fieldname': 'category', 'fieldtype': 'Data', 'width': 300},
        {'label': 'Occurrences', 'fieldname': 'fail_count', 'fieldtype': 'Int', 'width': 120},
    ]

    return columns, data
