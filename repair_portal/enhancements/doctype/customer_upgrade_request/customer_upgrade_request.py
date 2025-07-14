import frappe
from frappe.model.document import Document

class CustomerUpgradeRequest(Document):
    def on_submit(self):
        if not self.serial_no:
            return

        # PATCH: Ensure serial_no exists in ERPNext Serial No
        if not frappe.db.exists("Serial No", self.serial_no):
            frappe.throw(f"Serial No '{self.serial_no}' does not exist in ERPNext!")

        if not frappe.db.exists("Instrument Tracker", {"serial_no": self.serial_no}):
            return

        tracker = frappe.get_doc("Instrument Tracker", {"serial_no": self.serial_no})
        tracker.append(
            "interaction_logs",
            {
                "interaction_type": "Upgrade Request",
                "reference_doctype": "Customer Upgrade Request",
                "reference_name": self.name,
                "date": self.request_date,
                "notes": self.details or "",
            },
        )
        tracker.save(ignore_permissions=True)
