# repair_portal/config/repair_portal.py

from frappe import _

def get_data():
    return [
        {
            "module_name": "Repair Portal",
            "type": "module",
            "label": _("Repair Portal"),
            "icon": "octicon octicon-wrench",
            "color": "#5890ff",
            "link": "workspace/repair-portal",
            "default": 1
        }
    ]
