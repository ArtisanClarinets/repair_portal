# File Header Template
# Relative Path: repair_portal/inspection/doctype/instrument_inspection/instrument_inspection.py
# Last Updated: 2025-07-18
# Version: v1.0
# Purpose: Controller for Instrument Inspection DocType - handles validation, automation, and exception logging for all inspection scenarios (inventory, repair, maintenance, QA).
# Dependencies: frappe, Inspection Finding, Tenon Fit Assessment, Tone Hole Inspection Record

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from typing import Any


class InstrumentInspection(Document):
    """
    Controller for Instrument Inspection. Handles validation and custom automation.

    Args:
        Document (frappe.model.document.Document): Frappe Document base class
    Returns:
        None
    """

    def validate(self) -> None:
        """
        Validation hook to enforce business rules for each inspection type.
        Logs any exceptions for audit.
        """
        try:
            # Ensure serial_no is unique
            self._validate_unique_serial()
            # Required fields for New Inventory
            if self.inspection_type == 'New Inventory':
                missing = [
                    f
                    for f in ['manufacturer', 'model', 'key', 'wood_type']
                    if not getattr(self, f, None)
                ]
                if missing:
                    frappe.throw(
                        f"Missing required field(s) for New Inventory: {', '.join(missing)}"
                    )
            # Customer fields only for non-inventory
            if self.inspection_type == 'New Inventory' and (
                self.customer or self.preliminary_estimate
            ):
                frappe.throw(
                    'Customer and pricing fields must be empty for New Inventory inspections.'
                )
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), 'InstrumentInspection.validate')
            raise

    def _validate_unique_serial(self) -> None:
        """
        Ensures the serial_no is unique for the current inspection record.
        """
        if self.serial_no:
            duplicate = frappe.db.exists(
                'Instrument Inspection', {'serial_no': self.serial_no, 'name': ('!=', self.name)}
            )
            if duplicate:
                frappe.throw(
                    f'An Instrument Inspection already exists for Serial No: {self.serial_no}'
                )
