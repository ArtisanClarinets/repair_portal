# Report: Loaners Outstanding
# Module: Intake
# Updated: 2025-06-12

import frappe


def execute(filters=None):
    columns = [
        {'fieldname': 'loaner_serial', 'label': 'Loaner Serial', 'fieldtype': 'Data', 'width': 160},
        {
            'fieldname': 'issued_to',
            'label': 'Customer',
            'fieldtype': 'Link',
            'options': 'Customer',
            'width': 200,
        },
        {'fieldname': 'issued_date', 'label': 'Issued Date', 'fieldtype': 'Date', 'width': 120},
        {
            'fieldname': 'expected_return_date',
            'label': 'Expected Return',
            'fieldtype': 'Date',
            'width': 120,
        },
        {'fieldname': 'returned', 'label': 'Returned', 'fieldtype': 'Check', 'width': 100},
    ]

    data = frappe.get_all(
        'Loaner Instrument',
        filters={'returned': 0},
        fields=['loaner_serial', 'issued_to', 'issued_date', 'expected_return_date', 'returned'],
    )

    return columns, data
