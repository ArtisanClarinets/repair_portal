"""
File: repair_portal/client_profile/doctype/consent_log/consent_log.py
Last Updated: 2025-07-16
Version: 1.1
Purpose: Enforces required fields for Consent Log child table
Dependencies: frappe.model.document
"""

import frappe
from frappe.model.document import Document


class ConsentLog(Document):
    def validate(self):
        """Ensure that date and type are provided."""
        if not self.date_given:
            frappe.throw("Date Given is required.")
        if not self.consent_type:
            frappe.throw("Consent Type is required.")