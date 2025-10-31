# Path: repair_portal/repair_portal/doctype/estimate_upsell/estimate_upsell.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Estimate Upsell child table - manages estimate upsell items.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class EstimateUpsell(Document):
    """Child table controller for Estimate Upsell records."""

    def validate(self):
        """Validate estimate upsell requirements."""
        if not self.upsell_item:
            frappe.throw(_("Upsell Item is required"))
        if self.amount and self.amount < 0:
            frappe.throw(_("Amount cannot be negative"))