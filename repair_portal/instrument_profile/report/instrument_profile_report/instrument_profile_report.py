# Path: repair_portal/instrument_profile/report/instrument_profile_report/instrument_profile_report.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Script report for Instrument Profile with customer filtering; displays issue descriptions and basic profile data
# Dependencies: frappe

import frappe
from frappe import _


def execute(filters=None):
    data = frappe.db.get_all(
        'Instrument Profile',
        fields=['customer', 'issue_description'],
        filters={'customer': filters.get('customer')} if filters else {},
    )
    columns = [
        {'label': 'Customer', 'fieldname': 'customer', 'fieldtype': 'Data', 'width': 120},
        {
            'label': 'Issue Description',
            'fieldname': 'issue_description',
            'fieldtype': 'Data',
            'width': 200,
        },
    ]
    return columns, data
