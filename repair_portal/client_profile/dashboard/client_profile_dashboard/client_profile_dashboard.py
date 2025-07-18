# File Header Template
# Relative Path: repair_portal/client_profile/dashboard/client_profile_dashboard/client_profile_dashboard.py
# Last Updated: 2025-07-16
# Version: v1.1
# Purpose: Dashboard for Client Profile
# Dependencies: Player Profile, Instrument Profile, Leak Test, Repair Log, Intonation Session, Clarinet Setup Log, Clarinet Inspection

from frappe import _

def get_data():
    return {
        "fieldname": "customer",
        "transactions": [
            {
                "label": _("Players & Instruments"),
                "items": [
                    "Player Profile",
                    "Instrument Profile"
                ]
            },
            {
                "label": _("Repair History"),
                "items": [
                    "Repair Log",
                    "Clarinet Setup Log"
                ]
            },
            {
                "label": _("Lab Results"),
                "items": [
                    "Leak Test",
                    "Intonation Session"
                ]
            },
            {
                "label": _("QA Reports"),
                "items": [
                    "Clarinet Inspection"
                ]
            }
        ],
        "charts": [
            {
                "label": _("Repair Activity This Month"),
                "chart_type": "Bar",
                "data": {
                    "labels": ["Repair Log", "Setup Log"],
                    "datasets": [
                        {
                            "name": "Entries",
                            "values": [
                                "eval: frappe.db.count('Repair Log', {'customer': doc.customer, 'creation': [\">=\", frappe.utils.get_first_day(frappe.utils.nowdate())]})",
                                "eval: frappe.db.count('Clarinet Setup Log', {'customer': doc.customer, 'creation': [\">=\", frappe.utils.get_first_day(frappe.utils.nowdate())]})"
                            ]
                        }
                    ]
                },
                "colors": ["blue"]
            }
        ]
    }