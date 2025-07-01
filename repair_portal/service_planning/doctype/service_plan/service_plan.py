# relative path: service_planning/doctype/service_plan/service_plan.py
# last updated: 2025-07-01
# version: 1.1
# purpose: Controller for Service Plan DocType, handles submission and tracking linkage.

import frappe
from frappe.model.document import Document


class ServicePlan(Document):
    def on_submit(self):
        if not self.serial_number:
            return

        if not frappe.db.exists("Instrument Tracker", {"serial_number": self.serial_number}):
            return

        tracker = frappe.get_doc("Instrument Tracker", {"serial_number": self.serial_number})
        tracker.append(
            "interaction_logs",
            {
                "interaction_type": "Service Plan",
                "reference_doctype": "Service Plan",
                "reference_name": self.name,
                "date": self.plan_date,
                "notes": self.summary or "",
            },
        )
        tracker.save(ignore_permissions=True)
