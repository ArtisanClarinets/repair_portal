"""
File: repair_portal/customer/doctype/consent_log_entry/consent_log_entry.py
Last Updated: 2025-07-16
Version: 1.1
Purpose: Enforces required fields for Consent Log Entry child table
Dependencies: frappe.model.document
"""
from __future__ import annotations

import frappe
from frappe.model.document import Document


class ConsentLogEntry(Document):
    def validate(self):
        """Ensure that date and method are filled before saving."""
        if not self.entry_date:
            frappe.throw("Entry Date is required.")
        if not self.method:
            frappe.throw("Consent Method is required.")
