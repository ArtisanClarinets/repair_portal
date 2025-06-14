# Path: enhancements/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the Enhancements module for value-added service management

from frappe import _

def get_data():
    return [
        {
            "module_name": "Enhancements",
            "type": "module",
            "label": _("Enhancements"),
            "icon": "octicon octicon-plus",
            "color": "pink",
            "description": "Upgrades and enhancement options for clarinet repairs"
        }
    ]