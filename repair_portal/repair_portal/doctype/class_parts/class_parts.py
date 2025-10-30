# Path: repair_portal/repair_portal/doctype/class_parts/class_parts.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Class Parts child table - manages parts classification and categorization for repair operations.
# Dependencies: frappe, Item management

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ClassParts(Document):
    """
    Child table controller for Class Parts records.
    Manages parts classification and categorization.
    """

    def validate(self):
        """Validate parts classification."""
        if not self.item_code:
            frappe.throw(_("Item Code is required"))
            
        if self.qty and self.qty <= 0:
            frappe.throw(_("Quantity must be greater than zero"))
            
    def before_save(self):
        """Set defaults before saving."""
        if not self.qty:
            self.qty = 1.0