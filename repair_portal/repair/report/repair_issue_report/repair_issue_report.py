# File: repair_portal/repair_portal/repair/report/repair_issue_report/repair_issue_report.py
# Updated: 2025-06-28
# Version: 1.1
# Purpose: Script report for Repair Issue doctype

import frappe

def execute(filters=None):
    filters = filters or {}
    data = frappe.db.get_all(
        "Repair Issue",
        fields=["customer", "issue_description"],
        filters={"customer": filters.get("customer")} if filters.get("customer") else {}
    )
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 120},
        {"label": "Issue Description", "fieldname": "issue_description", "fieldtype": "Data", "width": 200}
    ]
    return columns, data