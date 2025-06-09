import frappe
from frappe.model.document import Document

class ClarinetConditionAssessment(Document):
    def on_submit(self):
        if not self.serial_number:
            return

        if not frappe.db.exists("Instrument Tracker", {"serial_number": self.serial_number}):
            return

        tracker = frappe.get_doc("Instrument Tracker", {"serial_number": self.serial_number})
        tracker.append("interaction_logs", {
            "interaction_type": "Inspection",
            "reference_doctype": "Clarinet Condition Assessment",
            "reference_name": self.name,
            "date": self.inspection_date,
            "notes": self.notes or ""
        })
        tracker.save(ignore_permissions=True)