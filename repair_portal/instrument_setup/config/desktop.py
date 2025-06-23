# Path: instrument_setup/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the Instrument Setup module for Frappe Desk

from frappe import _


def get_data():
    return [
        {
            'module_name': 'Instrument Setup',
            'type': 'module',
            'label': _('Instrument Setup'),
            'icon': 'octicon octicon-settings',
            'color': 'teal',
            'description': 'Reference data for clarinet models, parts, and specifications',
        }
    ]
