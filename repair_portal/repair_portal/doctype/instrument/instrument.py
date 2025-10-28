# Path: repair_portal/repair_portal/doctype/instrument/instrument.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Instrument - manages musical instrument records.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class Instrument(Document):
    """Controller for Instrument documents."""

    def validate(self):
        """Validate instrument requirements."""
        if not self.instrument_type:
            frappe.throw(_("Instrument Type is required"))
        if not self.brand:
            frappe.throw(_("Brand is required"))