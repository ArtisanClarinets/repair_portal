import frappe
from frappe.model.document import Document


class CustomerUpgradeRequest(Document):
    def on_submit(self):
        if not self.serial_number:
            return

        if not frappe.db.exists('Instrument Tracker', {'serial_number': self.serial_number}):
            return

        tracker = frappe.get_doc('Instrument Tracker', {'serial_number': self.serial_number})
        tracker.append(
            'interaction_logs',
            {
                'interaction_type': 'Upgrade Request',
                'reference_doctype': 'Customer Upgrade Request',
                'reference_name': self.name,
                'date': self.request_date,
                'notes': self.details or '',
            },
        )
        tracker.save(ignore_permissions=True)
