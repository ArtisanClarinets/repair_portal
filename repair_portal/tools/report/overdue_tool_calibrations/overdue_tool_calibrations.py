# Report: Overdue Tool Calibrations
# Module: Tools
# Updated: 2025-06-12

import frappe
from datetime import date

def execute(filters=None):
    columns = [
        {"fieldname": "tool_name", "label": "Tool Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "tool_type", "label": "Tool Type", "fieldtype": "Data", "width": 150},
        {"fieldname": "next_due", "label": "Next Calibration Due", "fieldtype": "Date", "width": 120},
        {"fieldname": "location", "label": "Location", "fieldtype": "Data", "width": 160}
    ]

    tools = frappe.db.get_all("Tool", fields=["tool_name", "tool_type", "next_due", "location"],
        filters={"requires_calibration": 1, "next_due": ("<", date.today())})

    return columns, tools