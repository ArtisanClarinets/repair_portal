# File: repair_portal/repair_portal/repair/report/repair_issue_report/repair_issue_report.py
# Updated: 2025-07-14
# Version: 2.0
# Purpose: Script report for Repair Order issues (unified doctype)

import frappe


def execute(filters=None):
    filters = filters or {}
    data = frappe.get_all(
        'Repair Order',
        fields=[
            'customer',
            'issue_description',
            'status',
            'technician_assigned',
            'priority_level',
            'promise_date',
        ],
        filters={'customer': filters.get('customer')} if filters.get('customer') else {},
    )
    columns = [
        {'label': 'Customer', 'fieldname': 'customer', 'fieldtype': 'Data', 'width': 120},
        {
            'label': 'Issue Description',
            'fieldname': 'issue_description',
            'fieldtype': 'Data',
            'width': 200,
        },
        {'label': 'Status', 'fieldname': 'status', 'fieldtype': 'Data', 'width': 100},
        {
            'label': 'Technician',
            'fieldname': 'technician_assigned',
            'fieldtype': 'Link',
            'options': 'User',
            'width': 120,
        },
        {'label': 'Priority', 'fieldname': 'priority_level', 'fieldtype': 'Data', 'width': 80},
        {'label': 'Promise Date', 'fieldname': 'promise_date', 'fieldtype': 'Date', 'width': 100},
    ]
    return columns, data
