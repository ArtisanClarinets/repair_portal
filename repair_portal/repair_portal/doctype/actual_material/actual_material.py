# Path: repair_portal/repair_portal/doctype/actual_material/actual_material.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Actual Material child table - manages actual materials used.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ActualMaterial(Document):
    """Child table controller for Actual Material records."""

    def validate(self):
        """Validate actual material requirements."""
        if not self.item_code:
            frappe.throw(_("Item Code is required"))
        if self.quantity and self.quantity <= 0:
            frappe.throw(_("Quantity must be greater than zero"))