# File: repair_portal/repair_portal/intake/report/loaner_turnover/loaner_turnover.py
# Updated: 2025-06-11
# Version: 1.0
# Purpose: Tracks the usage of loaner instruments over time

import frappe

def execute(filters=None):
    data = frappe.db.get_all("Clarinet Loaner Instrument", fields=["name", "customer", "loan_date", "return_date"])
    columns = [
        {"label": "Loaner ID", "fieldname": "name", "fieldtype": "Data", "width": 100},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
        {"label": "Loan Date", "fieldname": "loan_date", "fieldtype": "Date", "width": 120},
        {"label": "Return Date", "fieldname": "return_date", "fieldtype": "Date", "width": 120}
    ]
    return columns, data