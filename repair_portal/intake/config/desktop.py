# Path: repair_portal/intake/config/desktop.py
# Date: 2025-10-01
# Version: 1.0.0
# Description: Define the Intake module for the Frappe Desk UI; provides module icon, label, and description for navigation.
# Dependencies: frappe

from frappe import _


def get_data():
    return [
        {
            'module_name': 'Intake',
            'type': 'module',
            'label': _('Intake'),
            'icon': 'octicon octicon-sign-in',
            'color': 'grey',
            'description': 'Customer instrument intake workflows',
        }
    ]
