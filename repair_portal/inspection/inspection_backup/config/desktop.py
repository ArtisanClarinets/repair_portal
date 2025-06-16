# Path: inspection/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the Inspection module for the Frappe Desk UI

from frappe import _


def get_data():
    return [
        {
            'module_name': 'Inspection',
            'type': 'module',
            'label': _('Inspection'),
            'icon': 'octicon octicon-search',
            'color': 'green',
            'description': 'Visual and mechanical inspections of instruments',
        }
    ]
