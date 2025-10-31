# Path: repair_portal/repair_portal/doctype/intake_photo/intake_photo.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Intake Photo child table - handles photo validation and storage for instrument intake documentation.
# Dependencies: frappe, file handling utilities

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class IntakePhoto(Document):
    """
    Child table controller for Intake Photo records.
    Handles photo validation and storage for intake process.
    """

    def validate(self):
        """Validate photo requirements."""
        if not self.image:
            frappe.throw(_("Image is required"))
            
    def before_save(self):
        """Set default caption if empty."""
        if not self.caption and self.image:
            self.caption = f"Intake photo: {frappe.utils.now()}"