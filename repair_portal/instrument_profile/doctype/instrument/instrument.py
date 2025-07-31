# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument/instrument.py
# Last Updated: 2025-07-27
# Version: v1.1
# Purpose: Instrument DocType controller for validation, naming, and business logic for musical instrument records. Handles custom autoname generation for instrument_id.
# Dependencies: frappe.model.naming, Instrument Category Doctype, frappe.log_error

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Instrument(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        attachments: DF.AttachImage | None
        body_material: DF.Data | None
        brand: DF.Link | None
        clarinet_type: DF.Literal["B\u266d Clarinet", "A Clarinet", "E\u266d Clarinet", "Bass Clarinet", "Alto Clarinet", "Contrabass Clarinet", "Other"]
        current_status: DF.Literal["Active", "Needs Repair", "Awaiting Parts", "In Service", "Archived"]
        customer: DF.Link | None
        instrument_category: DF.Link | None
        instrument_id: DF.Data | None
        instrument_type: DF.Literal["B\u266d Clarinet", "A Clarinet", "Bass Clarinet", "E\u266d Clarinet", "Alto Clarinet", "Contrabass Clarinet", "Other"]
        key_plating: DF.Literal["Silver", "Nickel", "Gold", "Other"]
        keywork_plating: DF.Data | None
        model: DF.Data | None
        notes: DF.SmallText | None
        pitch_standard: DF.Data | None
        serial_no: DF.Data
        year_of_manufacture: DF.Int
    # end: auto-generated types
    """Instrument Document Model"""
    def validate(self):
        self.check_duplicate_serial_no()
        self.ensure_valid_instrument_category()
        self.set_instrument_id()
        self.autoname()

    def autoname(self):
        """
        Custom autoname logic to set instrument_id based on serial_no.
        If serial_no is not set, use default autoname.
        """
        if self.serial_no:
            self.set_instrument_id()
        else:
            self.name = make_autoname("INST-.####")
            self.set_instrument_id()
        return
    
    def check_duplicate_serial_no(self):
        # Avoid duplicate on current document!
        if self.serial_no and frappe.db.exists("Instrument", {"serial_no": self.serial_no, "name": ("!=", self.name)}):
            frappe.log_error(f"Duplicate Serial Number: {self.serial_no} found in Instrument records.")
            frappe.throw(f"Serial Number {self.serial_no} already exists in another Instrument record.")
        return

    def ensure_valid_instrument_category(self):
        if self.instrument_category:
            if not frappe.db.exists("Instrument Category", self.instrument_category):
                # Try to auto-patch with first active
                default = frappe.db.get_value("Instrument Category", {"is_active": 1}, "name")
                if default:
                    self.instrument_category = default
                else:
                    frappe.throw("Instrument Category is invalid and no active category found. Please select a valid category.")

    def set_instrument_id(self):
        """
        Generate unique instrument_id using the pattern INST-####-{serial_no}.
        Only set if not already set (create only, or if serial_no changed).
        """
        try:
            if not self.instrument_id or (self.serial_no and self.instrument_id and not self.instrument_id.endswith(self.serial_no)):
                next_seq = make_autoname("INST-.####")
                self.instrument_id = f"{next_seq}-{self.serial_no}"
        except Exception as e:
            frappe.log_error(f"Instrument ID Auto-generation failed: {str(e)}", "Instrument: set_instrument_id")
            frappe.throw("Unable to generate Instrument ID. Please contact your administrator.")
