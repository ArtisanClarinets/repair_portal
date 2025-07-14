# relative path: service_planning/doctype/service_plan/service_plan.py
# last updated: 2025-07-01
# version: 1.1
# purpose: Controller for Service Plan DocType, handles submission and tracking linkage.

import frappe
from frappe.model.document import Document


class ServicePlan(Document):
    def on_submit(self):
        if not self.serial_no:
            return

        # Ensure serial_no exists in ERPNext Serial No doctype
        if not frappe.db.exists("Serial No", self.serial_no):
            frappe.throw(f"Serial No '{self.serial_no}' does not exist in ERPNext. Please select a valid Serial No.")

        if not frappe.db.exists("Instrument Tracker", {"serial_no": self.serial_no}):
            return

        tracker = frappe.get_doc("Instrument Tracker", {"serial_no": self.serial_no})
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
