# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument/instrument.py
# Last Updated: 2025-08-01
# Version: v1.2
# Purpose: Optimized Instrument DocType controller to reduce database calls and redundant autoname execution during save. Handles validation, naming, and business logic for musical instrument records.
# Dependencies: frappe.model.naming, Instrument Category Doctype, frappe.log_error

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

# Cache for active instrument category to minimize DB lookups
_active_category_cache: str | None = None

class Instrument(Document):
    """Instrument Document Model with optimized validation and naming."""

    def validate(self):
        """
        Validation logic executed on every save.
        Optimized to avoid unnecessary DB calls and duplicate operations.
        """
        # Only check for duplicate serial number if it's a new document or serial number changed
        if self.is_new() or self.has_value_changed("serial_no"):
            self.check_duplicate_serial_no()
            self.set_instrument_id()

        # Validate instrument category
        self.ensure_valid_instrument_category()

    def autoname(self):
        """
        Generate a name for the document using series.
        Runs only once, avoids duplicate calls inside validate.
        """
        if not self.name:
            self.name = make_autoname("INST-.####")

    def check_duplicate_serial_no(self):
        """
        Ensure serial_no is unique across all Instrument records.
        Avoids duplicate queries if serial_no unchanged.
        """
        if self.serial_no:
            if frappe.db.exists("Instrument", {"serial_no": self.serial_no, "name": ("!=", self.name)}):
                frappe.log_error(f"Duplicate Serial Number: {self.serial_no} found in Instrument records.")
                frappe.throw(f"Serial Number {self.serial_no} already exists in another Instrument record.")

    def ensure_valid_instrument_category(self):
        """
        Validate instrument_category link. If invalid, patch with first active category if available.
        Uses cached value to reduce DB calls.
        """
        global _active_category_cache

        if self.instrument_category and not frappe.db.exists("Instrument Category", self.instrument_category):
            if not _active_category_cache:
                _active_category_cache = frappe.db.get_value("Instrument Category", {"is_active": 1}, "name")
            if _active_category_cache:
                self.instrument_category = _active_category_cache
            else:
                frappe.throw("Instrument Category is invalid and no active category found. Please select a valid category.")

    def set_instrument_id(self):
        """
        Generate a unique instrument_id using the pattern INST-####-{serial_no}.
        Only regenerate if serial_no is set and changed or instrument_id is empty.
        """
        try:
            if self.serial_no:
                if (not self.instrument_id) or (self.instrument_id and not self.instrument_id.endswith(self.serial_no)):
                    next_seq = make_autoname("INST-.####")
                    self.instrument_id = f"{next_seq}-{self.serial_no}"
        except Exception as e:
            frappe.log_error(f"Instrument ID Auto-generation failed: {str(e)}", "Instrument: set_instrument_id")
            frappe.throw("Unable to generate Instrument ID. Please contact your administrator.")