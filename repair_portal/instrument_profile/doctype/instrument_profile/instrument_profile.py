# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-14
# Version: 1.0
# Purpose: Server-side logic for Instrument Profile Doctype

import frappe
from frappe.model.document import Document

class InstrumentProfile(Document):
    def validate(self):
        if not self.customer:
            frappe.throw("Customer is required")

    def on_submit(self):
        frappe.msgprint("Instrument Profile submitted.")
