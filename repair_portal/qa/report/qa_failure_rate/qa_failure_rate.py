# Report: QA Failure Rate
# Module: QA
# Updated: 2025-06-12

import frappe


def execute(filters=None):
    columns = [
        {
            "fieldname": "qa_technician",
            "label": "QA Technician",
            "fieldtype": "Link",
            "options": "User",
            "width": 200,
        },
        {"fieldname": "total_checks", "label": "Total QA Checks", "fieldtype": "Int", "width": 160},
        {"fieldname": "failures", "label": "Failures", "fieldtype": "Int", "width": 100},
        {"fieldname": "failure_rate", "label": "Failure Rate (%)", "fieldtype": "Percent", "width": 140},
    ]

    data = []
    qa_list = frappe.db.sql(
        """
        SELECT qa_technician,
               COUNT(name) AS total_checks,
               SUM(CASE WHEN overall_passed = 0 THEN 1 ELSE 0 END) AS failures,
               ROUND(SUM(CASE WHEN overall_passed = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(name), 2) AS failure_rate
        FROM `tabFinal QA Checklist`
        GROUP BY qa_technician
    """,
        as_dict=True,
    )

    for row in qa_list:
        data.append(row)

    return columns, data
