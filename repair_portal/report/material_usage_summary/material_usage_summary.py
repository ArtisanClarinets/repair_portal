# File: repair_portal/report/material_usage_summary/material_usage_summary.py
# Updated: 2025-06-16
# Version: 1.0
# Purpose: Summary of material use across repair logs (pads, springs, cork, etc.)

import frappe


def execute(filters=None):
    columns = [
        {"label": "Repair Log", "fieldname": "parent", "fieldtype": "Link", "options": "Clarinet Repair Log", "width": 120},
        {"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Used On", "fieldname": "used_on", "fieldtype": "Data", "width": 120},
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 200}
    ]

    data = frappe.db.get_all(
        "Material Use Log",
        fields=["parent", "item_code", "used_on", "qty", "remarks"],
        order_by="modified desc"
    )

    return columns, data