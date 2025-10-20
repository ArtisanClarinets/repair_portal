# Path: service_planning/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the Service Planning module for the Frappe Desk UI

from frappe import _


def get_data():
    return [
        {
            "module_name": "Service Planning",
            "type": "module",
            "label": _("Service Planning"),
            "icon": "octicon octicon-calendar",
            "color": "orange",
            "description": "Scheduling and management of clarinet service jobs",
        }
    ]
