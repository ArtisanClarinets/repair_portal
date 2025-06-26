# Path: repair_logging/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the Repair Logging module for the Frappe Desk UI

from frappe import _


def get_data():
    return [
        {
            "module_name": "Repair Logging",
            "type": "module",
            "label": _("Repair Logging"),
            "icon": "octicon octicon-tools",
            "color": "purple",
            "description": "Logging and tracking of repair procedures",
        }
    ]
