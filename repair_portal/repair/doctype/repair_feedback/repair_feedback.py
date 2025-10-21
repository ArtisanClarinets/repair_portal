# File: repair_portal/repair/doctype/repair_feedback/repair_feedback.py
# Created: 2025-06-15
# Version: 1.0
# Purpose: Backend logic for storing customer repair feedback
from __future__ import annotations

import frappe
from frappe.model.document import Document


class RepairFeedback(Document):
    def validate(self):
        if not self.repair_order:  # type: ignore
            frappe.throw("Repair Order is required.")
        if not 1 <= int(self.rating) <= 5:  # type: ignore
            frappe.throw("Rating must be between 1 and 5.")
