import frappe
from frappe.model.document import Document

class ServicePlan(Document):

    def validate(self):
        if not self.item_code:
            frappe.throw("Instrument must be selected for the service plan.")

        if not self.requested_services:
            frappe.throw("Please add at least one requested service.")