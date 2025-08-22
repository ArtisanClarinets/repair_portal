# File: repair_portal/instrument_profile/report/instrument_inventory_report/instrument_inventory_report.py
# Created: 2025-06-13
# Version: 1.0
# Purpose: Script report showing instrument inventory by type, acquisition, and status

import frappe


def execute(filters=None):
    filters = filters or {}
    conditions = {}
    if filters.get('acquisition_type'):
        conditions['acquisition_type'] = filters['acquisition_type']
    if filters.get('status'):
        conditions['status'] = filters['status']
    if filters.get('customer'):
        conditions['customer'] = filters['customer']

    data = frappe.db.get_all(
        'Instrument Profile',
        fields=[
            'name',
            'instrument_category',
            'model',
            'serial_no',
            'status',
            'acquisition_type',
            'customer',
        ],
        filters=conditions,
    )

    columns = [
        {
            'label': 'Instrument ID',
            'fieldname': 'name',
            'fieldtype': 'Link',
            'options': 'Instrument Profile',
            'width': 140,
        },
        {'label': 'Type', 'fieldname': 'instrument_category', 'fieldtype': 'Data'},
        {'label': 'Model', 'fieldname': 'model', 'fieldtype': 'Data'},
        {'label': 'Serial', 'fieldname': 'serial_no', 'fieldtype': 'Link', 'options': 'Serial No'},
        {'label': 'Status', 'fieldname': 'status', 'fieldtype': 'Select'},
        {'label': 'Acquisition', 'fieldname': 'acquisition_type', 'fieldtype': 'Select'},
        {'label': 'Customer', 'fieldname': 'customer', 'fieldtype': 'Link', 'options': 'Customer'},
    ]

    return columns, data
