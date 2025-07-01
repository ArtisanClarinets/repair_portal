# File: repair_portal/repair/report/repair_revenue_vs_cost/repair_revenue_vs_cost.py
# Updated: 2025-06-15
# Version: 1.0
# Purpose: Script Report showing repair revenue vs cost

import frappe


def execute(filters=None):
    conditions = []
    if filters.get("from_date"):
        conditions.append(f"ro.creation >= '{filters['from_date']}'")
    if filters.get("to_date"):
        conditions.append(f"ro.creation <= '{filters['to_date']}'")
    where_clause = f'WHERE {" AND ".join(conditions)}' if conditions else ""

    data = frappe.db.sql(
        f"""
        SELECT
            ro.name AS repair_order,
            ro.total_parts_cost,
            ro.total_labor_hours * 50 AS labor_value, -- Assume $50/hour
            (ro.total_parts_cost + ro.total_labor_hours * 50) AS total_cost
        FROM `tabRepair Order` ro
        {where_clause}
    """,
        as_dict=True,
    )

    columns = [
        {
            "label": "Repair Order",
            "fieldname": "repair_order",
            "fieldtype": "Link",
            "options": "Repair Order",
        },
        {"label": "Parts Cost", "fieldname": "total_parts_cost", "fieldtype": "Currency"},
        {"label": "Labor Value ($50/hr)", "fieldname": "labor_value", "fieldtype": "Currency"},
        {"label": "Total Cost", "fieldname": "total_cost", "fieldtype": "Currency"},
    ]

    return columns, data
