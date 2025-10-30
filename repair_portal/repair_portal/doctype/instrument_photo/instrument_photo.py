# Path: repair_portal/repair_portal/doctype/instrument_photo/instrument_photo.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Instrument Photo child table - manages instrument photos.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class InstrumentPhoto(Document):
    """Child table controller for Instrument Photo records."""

    def validate(self):
        """Validate instrument photo requirements."""
        if not self.photo:
            frappe.throw(_("Photo is required"))
        
        # Validate file format
        if self.photo and not self.photo.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            frappe.throw(_("Photo must be in JPG, PNG, or GIF format"))