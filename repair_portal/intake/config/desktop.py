# Path: intake/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the Intake module for the Frappe Desk UI

from frappe import _

def get_data():
    return [
        {
            "module_name": "Intake",
            "type": "module",
            "label": _("Intake"),
            "icon": "octicon octicon-sign-in",
            "color": "grey",
            "description": "Customer instrument intake workflows"
        }
    ]