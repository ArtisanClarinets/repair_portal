# File: repair_portal/intake/doctype/loaner_instrument/loaner_instrument.py
# Date Updated: 2025-06-12
# Version: v1.0
# Purpose: Server-side controller for Loaner Instrument - validation and issue handling

import frappe
from frappe.model.document import Document

class LoanerInstrument(Document):
    def validate(self):
        if self.returned and not self.expected_return_date:
            frappe.throw("Expected return date must be set before marking as returned.")