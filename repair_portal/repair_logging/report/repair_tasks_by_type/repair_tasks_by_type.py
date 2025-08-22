# ---------------------------------------------------------------------------
# Report: Repair Tasks by Type
# File: repair_portal/repair_logging/report/repair_tasks_by_type/repair_tasks_by_type.py
# Date Updated: 2025-07-02
# Version: v1.2
# Purpose: Adds date range and technician filters, and chart data.
# ---------------------------------------------------------------------------

import frappe


def execute(filters=None):
    if filters is None:
        filters = {}

    conditions = []
    params = {}

    if filters.get('from_date'):
        conditions.append('creation >= %(from_date)s')
        params['from_date'] = filters['from_date']

    if filters.get('to_date'):
        conditions.append('creation <= %(to_date)s')
        params['to_date'] = filters['to_date']

    if filters.get('assigned_to'):
        conditions.append('assigned_to = %(assigned_to)s')
        params['assigned_to'] = filters['assigned_to']

    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''

    data = frappe.db.sql(
        f"""
        SELECT
            task_type,
            COUNT(name) AS task_count
        FROM
            `tabRepair Task Log`
        {where_clause}
        GROUP BY
            task_type
        """,
        params,
        as_dict=True,
    )

    columns = [
        {'fieldname': 'task_type', 'label': 'Task Type', 'fieldtype': 'Data', 'width': 200},
        {'fieldname': 'task_count', 'label': 'Task Count', 'fieldtype': 'Int', 'width': 120},
    ]

    chart = {
        'data': {
            'labels': [row['task_type'] for row in data],  # type: ignore
            'datasets': [
                {
                    'name': 'Task Count',
                    'values': [row['task_count'] for row in data],  # type: ignore
                }
            ],
        },
        'type': 'bar',
    }

    return columns, data, None, chart
