import frappe
from frappe.model.document import Document

class ClarinetIntake(Document):
    def on_submit(self):
        tracker = frappe.get_doc({
            "doctype": "Instrument Tracker",
            "serial_number": self.serial_number
        }) if frappe.db.exists("Instrument Tracker", {"serial_number": self.serial_number}) else frappe.get_doc({
            "doctype": "Instrument Tracker",
            "serial_number": self.serial_number,
            "item_code": self.item_code,
            "customer": self.customer,
            "clarinet_intake": self.name,
            "intake_date": self.received_date
        })

        tracker.append("interaction_logs", {
            "interaction_type": "Intake",
            "reference_doctype": "Clarinet Intake",
            "reference_name": self.name,
            "date": self.received_date,
            "notes": self.customer_notes or ""
        })

        tracker.save(ignore_permissions=True)
