# File: repair_portal/repair_portal/lab/report/custom_doctype_report/custom_doctype_report.py
# Updated: 2025-06-20
# Version: 1.1
# Purpose: Script report for Custom Doctype with extended filters and summary row

import frappe


def execute(filters=None):
    filters = filters or {}
    conditions = {}
    if filters.get("customer"):
        conditions["customer"] = filters["customer"]
    if filters.get("status"):
        conditions["status"] = filters["status"]

    data = frappe.db.get_all("Custom Doctype", fields=["customer", "issue_description", "status"], filters=conditions)
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 120},
        {"label": "Issue Description", "fieldname": "issue_description", "fieldtype": "Data", "width": 200},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100}
    ]
    
    if data:
        data.append({"customer": "---", "issue_description": "Total Issues", "status": len(data)})

    return columns, data