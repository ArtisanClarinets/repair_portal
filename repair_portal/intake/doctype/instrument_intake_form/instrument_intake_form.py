import frappe
from frappe.model.document import Document

class InstrumentIntakeForm(Document):

    def validate(self):
        if not self.customer or not self.instrument:
            frappe.throw("Customer and Instrument must be specified.")

        if not self.terms_accepted:
            frappe.throw("Customer must accept terms before submission.")

        if not self.signature:
            frappe.throw("Signature is required.")

    def before_save(self):
        if not self.intake_received_by:
            self.intake_received_by = frappe.session.user