# File: repair_portal/repair_portal/intake/report/followup_compliance/followup_compliance.py
# Updated: 2025-06-11
# Version: 1.0
# Purpose: Analyze compliance rate of intake followups

import frappe


def execute(filters=None):
    data = frappe.db.get_all('Intake Followup', fields=['customer', 'status', 'followup_date'])
    columns = [
        {
            'label': 'Customer',
            'fieldname': 'customer',
            'fieldtype': 'Link',
            'options': 'Customer',
            'width': 180,
        },
        {'label': 'Status', 'fieldname': 'status', 'fieldtype': 'Data', 'width': 100},
        {
            'label': 'Follow-up Date',
            'fieldname': 'followup_date',
            'fieldtype': 'Date',
            'width': 120,
        },
    ]
    return columns, data
