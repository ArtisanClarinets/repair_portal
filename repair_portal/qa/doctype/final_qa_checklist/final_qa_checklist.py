import frappe
from frappe.model.document import Document

class FinalQAChecklist(Document):
    def on_submit(self):
        if not self.serial_number:
            return

        if not frappe.db.exists("Instrument Tracker", {"serial_number": self.serial_number}):
            return

        tracker = frappe.get_doc("Instrument Tracker", {"serial_number": self.serial_number})
        tracker.append("interaction_logs", {
            "interaction_type": "QA Check",
            "reference_doctype": "Final QA Checklist",
            "reference_name": self.name,
            "date": self.qa_date,
            "notes": self.technician_notes or ""
        })
        tracker.save(ignore_permissions=True)