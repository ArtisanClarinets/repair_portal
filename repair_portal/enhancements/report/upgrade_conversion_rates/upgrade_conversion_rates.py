# File: repair_portal/repair_portal/enhancements/report/upgrade_conversion_rates/upgrade_conversion_rates.py
# Updated: 2025-06-12
# Version: 1.0
# Purpose: Aggregate upgrade request statuses for conversion insights

import frappe

def execute(filters=None):
    data = frappe.db.sql("""
        SELECT customer, status, COUNT(*) as count
        FROM `tabCustomer Upgrade Request`
        GROUP BY customer, status
    """, as_dict=True)

    columns = [
        {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
        {"fieldname": "count", "label": "Requests", "fieldtype": "Int", "width": 120}
    ]

    return columns, data