# File: repair_portal/repair_portal/repair_logging/doctype/warranty/warranty.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Handles Warranty validation and logic

import frappe
from frappe.model.document import Document


class Warranty(Document):
    def validate(self):
        if not self.instrument or not self.warranty_expiry_date:
            frappe.throw("Instrument and expiry date must be set.")