# Path: repair_portal/repair_portal/doctype/shipment/shipment.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Shipment - manages shipping and logistics for instrument delivery and returns.
# Dependencies: frappe, logistics integration

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class Shipment(Document):
    """Controller for Shipment DocType."""

    def validate(self):
        """Validate shipment requirements."""
        if not self.customer:
            frappe.throw(_("Customer is required"))
            
    def before_save(self):
        """Set default status."""
        if not self.status:
            self.status = "Draft"