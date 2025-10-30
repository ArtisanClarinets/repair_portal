# Path: repair_portal/repair_portal/doctype/repair_estimate/repair_estimate.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Repair Estimate - manages repair cost estimates.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class RepairEstimate(Document):
    """Controller for Repair Estimate documents."""

    def validate(self):
        """Validate repair estimate requirements."""
        if not self.customer:
            frappe.throw(_("Customer is required"))
        if not self.instrument:
            frappe.throw(_("Instrument is required"))
        if self.total_cost and self.total_cost < 0:
            frappe.throw(_("Total Cost cannot be negative"))