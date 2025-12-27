# File: repair_portal/repair/report/repair_revenue_vs_cost/repair_revenue_vs_cost.py
# Updated: 2025-07-13
# Version: 1.1
# Purpose: Script Report showing repair revenue vs cost (parameterized and secure)

import frappe


def execute(filters=None):
    filters = filters or {}
    conditions = []

    if filters.get('from_date'):
        conditions.append('ro.creation >= %(from_date)s')
    if filters.get('to_date'):
        conditions.append('ro.creation <= %(to_date)s')

    where_clause = f'WHERE {" AND ".join(conditions)}' if conditions else ''

    # Bolt: Fetch the default labor rate from Repair Settings once to avoid
    # hardcoding it and to ensure a single source of truth. Using get_single_value
    # is efficient as it caches the result.
    labor_rate = frappe.db.get_single_value('Repair Settings', 'default_labor_rate') or 50.0

    query = f"""
        SELECT
            ro.name AS repair_order,
            ro.total_parts_cost,
            ro.total_labor_hours * %(labor_rate)s AS labor_value,
            (ro.total_parts_cost + ro.total_labor_hours * %(labor_rate)s) AS total_cost
        FROM `tabRepair Order` ro
        {where_clause}
    """
    filters['labor_rate'] = labor_rate

    data = frappe.db.sql(query, filters, as_dict=True)

    columns = [
        {
            'label': 'Repair Order',
            'fieldname': 'repair_order',
            'fieldtype': 'Link',
            'options': 'Repair Order',
        },
        {'label': 'Parts Cost', 'fieldname': 'total_parts_cost', 'fieldtype': 'Currency'},
        {'label': 'Labor Value ($50/hr)', 'fieldname': 'labor_value', 'fieldtype': 'Currency'},
        {'label': 'Total Cost', 'fieldname': 'total_cost', 'fieldtype': 'Currency'},
    ]

    return columns, data
