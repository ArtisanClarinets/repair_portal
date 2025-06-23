# File: repair_portal/repair_portal/report/customer_issue_log_report/customer_issue_log_report.py
# Updated: 2025-06-21
# Version: 1.2
# Purpose: Script report for Customer Issue Log

import frappe


def execute(filters=None):
    data = frappe.db.get_all("Customer Issue Log",
        fields=["customer", "issue_description"],
        filters={"customer": filters.get("customer")} if filters else {}
    )
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 120},
        {"label": "Issue Description", "fieldname": "issue_description", "fieldtype": "Data", "width": 200}
    ]
    return columns, data