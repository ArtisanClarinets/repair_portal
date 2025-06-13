# File: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Created: 2025-06-13
# Version: 1.0
# Purpose: Controller logic for Instrument Profile DocType

import frappe
from frappe.model.document import Document

class InstrumentProfile(Document):
    def validate(self):
        if self.acquisition_type == "Customer" and not self.customer:
            frappe.throw("Customer is required for customer-owned instruments.")

    def on_submit(self):
        frappe.msgprint("Instrument profile submitted successfully.")
