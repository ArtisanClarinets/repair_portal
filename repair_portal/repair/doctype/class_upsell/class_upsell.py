# Path: repair_portal/repair_portal/doctype/class_upsell/class_upsell.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Class Upsell child table - manages upsell recommendations.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ClassUpsell(Document):
    """Child table controller for Class Upsell records."""

    def validate(self):
        """Validate upsell requirements."""
        if not self.upsell_item:
            frappe.throw(_("Upsell Item is required"))