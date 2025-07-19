# File Header Template
# Relative Path: repair_portal/repair_logging/doctype/instrument_photo/instrument_photo.py
# Last Updated: 2025-07-17
# Version: v1.0
# Purpose: Controller for Instrument Photo child table, enforcing robust data integrity, audit, and user guidance for instrument image documentation.
# Dependencies: frappe, frappe.log_error

"""
InstrumentPhoto Controller
------------------------
This Document controller enforces that every photo is labeled, ensures required images are present, and logs all exceptions for audit. For use within Instrument Profile and any other parent doctypes needing photo logs.

Best Practices:
- Required fields enforced: image, label.
- Notes are optional but recommended for clarity in QA.
- Audit trail via Frappe built-ins.
- All exceptions logged for traceability (Fortune 500 standard).
"""

import frappe
from frappe.model.document import Document


class InstrumentPhoto(Document):
    def validate(self) -> None:
        """
        Validates required fields and logs exceptions for missing critical info.
        """
        try:
            if not self.image:
                frappe.throw('Instrument Photo: Image is required.')
            if not self.label:
                frappe.throw("Instrument Photo: Label is required (e.g., 'Bell', 'Serial Number').")
        except Exception:
            frappe.log_error(frappe.get_traceback(), 'InstrumentPhoto: Validation Error')
            raise
