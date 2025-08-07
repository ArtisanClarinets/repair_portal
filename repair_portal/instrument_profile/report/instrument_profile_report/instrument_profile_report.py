# File: repair_portal/repair_portal/instrument_profile/report/instrument_profile_report/instrument_profile_report.py
# Updated: 2025-06-14
# Version: 1.0
# Purpose: Script report for Instrument Profile

import frappe


def execute(filters=None):
    data = frappe.db.get_all(
        "Instrument Profile",
        fields=["customer", "issue_description"],
        filters={"customer": filters.get("customer")} if filters else {},
    )
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 120},
        {
            "label": "Issue Description",
            "fieldname": "issue_description",
            "fieldtype": "Data",
            "width": 200,
        },
    ]
    return columns, data
