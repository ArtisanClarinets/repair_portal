# Path: repair_portal/instrument_profile/config/desktop.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Desktop workspace configuration for Instrument Profile module; defines module card appearance and links
# Dependencies: frappe


def get_data():
    return [
        {
            "module_name": "Instrument Profile",
            "label": "Instrument Profile",
            "color": "blue",
            "icon": "octicon octicon-device-camera",
            "type": "module",
            "description": "Instrument profiles for clients and inventory.",
        }
    ]
