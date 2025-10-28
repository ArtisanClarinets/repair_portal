# Path: repair_portal/repair_portal/doctype/rental_inspection_finding/rental_inspection_finding.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Rental Inspection Finding child table - manages rental inspection findings.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class RentalInspectionFinding(Document):
    """Child table controller for Rental Inspection Finding records."""

    def validate(self):
        """Validate inspection finding requirements."""
        if not self.finding:
            frappe.throw(_("Finding is required"))