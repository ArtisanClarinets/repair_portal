# File: repair_portal/repair_portal/inspection/report/inspection_failure_rates/inspection_failure_rates.py
# Updated: 2025-06-12
# Version: 1.0
# Purpose: Generate technician-wise failure counts and rates for condition assessments

import frappe

def execute(filters=None):
    results = frappe.db.sql("""
        SELECT technician,
               SUM(CASE WHEN instrument_condition != 'Good' THEN 1 ELSE 0 END) AS fail_count,
               COUNT(*) AS total,
               ROUND(SUM(CASE WHEN instrument_condition != 'Good' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fail_rate
        FROM `tabClarinet Condition Assessment`
        WHERE docstatus = 1
        GROUP BY technician
    """, as_dict=True)

    columns = [
        {"label": "Technician", "fieldname": "technician", "fieldtype": "Link", "options": "User", "width": 200},
        {"label": "Failures", "fieldname": "fail_count", "fieldtype": "Int", "width": 120},
        {"label": "Total Inspections", "fieldname": "total", "fieldtype": "Int", "width": 150},
        {"label": "Failure Rate %", "fieldname": "fail_rate", "fieldtype": "Percent", "width": 130}
    ]

    return columns, results