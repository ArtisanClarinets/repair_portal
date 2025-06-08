from frappe import _

def get_data():
    return [
        {
            "label": _("Repair Portal"),
            "items": [
                {"type": "module", "name": "Repair Portal", "label": _("Overview")},
                {"type": "workspace", "name": "intake-workspace", "label": _("Intake")},
                {"type": "workspace", "name": "inspection-workspace", "label": _("Inspection")},
                {"type": "workspace", "name": "service-planning-workspace", "label": _("Service Planning")},
                {"type": "workspace", "name": "repair-logging-workspace", "label": _("Repair Logging")},
                {"type": "workspace", "name": "qa-workspace", "label": _("Final QA")},
                {"type": "workspace", "name": "repair-tools-workspace", "label": _("Repair Tools")},
                {"type": "workspace", "name": "repair-enhancements-workspace", "label": _("Repair Enhancements")}
            ]
        }
    ]