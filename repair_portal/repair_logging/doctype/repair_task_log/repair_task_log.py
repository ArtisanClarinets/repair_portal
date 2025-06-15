"""
repair_logging/doctype/repair_task_log/repair_task_log.py
Repair Task Log
Version 1.0
Last Updated: 2025-06-09

Logs individual repair actions. On submission, updates the Instrument Tracker with a corresponding interaction log entry.
"""

import frappe
from frappe.model.document import Document


class RepairTaskLog(Document):
    def on_submit(self):
        if not self.serial_number:
            return

        if not frappe.db.exists("Instrument Tracker", {"serial_number": self.serial_number}):
            return

        tracker = frappe.get_doc("Instrument Tracker", {"serial_number": self.serial_number})
        tracker.append(
            "interaction_logs",
            {
                "interaction_type": "Repair",
                "reference_doctype": "Repair Task Log",
                "reference_name": self.name,
                "date": self.task_date,
                "notes": self.notes or "",
            },
        )
        tracker.save(ignore_permissions=True)
