# File: repair_portal/repair_portal/intake/report/deposit_balance_aging/deposit_balance_aging.py
# Updated: 2025-06-11
# Version: 1.0
# Purpose: Script Report for deposit balance aging by customer

import frappe

def execute(filters=None):
    data = frappe.db.sql("""
        SELECT customer, SUM(deposit_amount - used_amount) AS balance
        FROM `tabClarinet Intake`
        GROUP BY customer
    """, as_dict=True)
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
        {"label": "Balance", "fieldname": "balance", "fieldtype": "Currency", "width": 120}
    ]
    return columns, data