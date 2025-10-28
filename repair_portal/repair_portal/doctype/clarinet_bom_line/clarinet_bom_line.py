# Path: repair_portal/repair_portal/doctype/clarinet_bom_line/clarinet_bom_line.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Clarinet BOM Line child table - manages BOM line items.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ClarinetBomLine(Document):
    """Child table controller for Clarinet BOM Line records."""

    def validate(self):
        """Validate BOM line requirements."""
        if not self.item_code:
            frappe.throw(_("Item Code is required"))
        if self.quantity and self.quantity <= 0:
            frappe.throw(_("Quantity must be greater than zero"))