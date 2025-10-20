# Path: repair_portal/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the Repair Portal module for top-level navigation in Frappe Desk

from frappe import _


def get_data():
    return [
        {
            "module_name": "Repair Portal",
            "type": "module",
            "label": _("Repair Portal"),
            "icon": "octicon octicon-tools",
            "color": "blue",
            "description": "Main navigation module for Clarinet Repair Portal",
        }
    ]
