# File: repair_portal/repair_portal/intake/report/intake_by_day/intake_by_day.py
# Updated: 2025-06-11
# Version: 1.0
# Purpose: Shows number of intakes submitted each day

import frappe

def execute(filters=None):
    data = frappe.db.sql("""
        SELECT DATE(intake_date) AS date, COUNT(*) AS count
        FROM `tabClarinet Intake`
        GROUP BY DATE(intake_date)
        ORDER BY date DESC
    """, as_dict=True)
    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": "Intake Count", "fieldname": "count", "fieldtype": "Int", "width": 100}
    ]
    return columns, data