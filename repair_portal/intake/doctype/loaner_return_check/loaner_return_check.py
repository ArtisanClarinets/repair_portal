# File: repair_portal/intake/doctype/loaner_return_check/loaner_return_check.py
# Date Updated: 2025-06-12
# Version: v1.0
# Purpose: Server-side controller for Loaner Return Check - manages post-save and validation logic

import frappe
from frappe.model.document import Document


class LoanerReturnCheck(Document):
    def validate(self):
        if self.damage_found and not self.condition_notes:
            frappe.throw('Please include condition notes when damage is flagged.')
