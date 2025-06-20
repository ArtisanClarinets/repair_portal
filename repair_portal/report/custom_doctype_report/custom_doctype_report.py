# File: repair_portal/repair_portal/report/custom_doctype_report/custom_doctype_report.py
# Updated: 2025-06-20
# Version: 1.1
# Purpose: Script report for Custom Doctype – Customer issue overview

import frappe

def execute(filters=None):
    data = frappe.db.get_all("Custom Doctype",
        fields=["customer", "issue_description"],
        filters={"customer": filters.get("customer")} if filters else {}
    )
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 120},
        {"label": "Issue Description", "fieldname": "issue_description", "fieldtype": "Data", "width": 200}
    ]
    return columns, data