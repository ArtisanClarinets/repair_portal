# Path: tools/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the Tools module for developer/admin tools on Frappe Desk

from frappe import _


def get_data():
    return [
        {
            'module_name': 'Tools',
            'type': 'module',
            'label': _('Tools'),
            'icon': 'octicon octicon-terminal',
            'color': 'darkgrey',
            'description': 'Developer and technician tools for diagnostics and utilities',
        }
    ]
