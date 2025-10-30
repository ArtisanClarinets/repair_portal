# Path: repair_portal/repair_portal/doctype/clarinet_intake/clarinet_intake.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Clarinet Intake - manages clarinet instrument intake workflow.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ClarinetIntake(Document):
    """Controller for Clarinet Intake documents."""

    def validate(self):
        """Validate clarinet intake requirements."""
        if not self.get("customer"):
            frappe.throw(_("Customer is required"))
        if not self.get("instrument"):
            frappe.throw(_("Instrument is required"))
        if not self.get("condition_grade"):
            frappe.throw(_("Condition Grade is required"))

    def before_save(self):
        """Operations before saving the intake."""
        self.generate_barcode()

    def generate_barcode(self):
        """Generate barcode for tracking."""
        if not self.get("barcode"):
            self.db_set("barcode", self.name)