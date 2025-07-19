# Path: repair_portal/lab/config/desktop.py
# Version: 1.0
# Updated: 2025-06-17
# Purpose: Desk module definition for Lab tools

from frappe import _


def get_data():
    return [
        {
            'module_name': 'Lab',
            'label': _('Lab'),
            'color': 'orange',
            'icon': 'octicon octicon-graph',
            'type': 'module',
            'description': 'Audio analysis tools for instruments',
        }
    ]
