# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Instrument(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from frappe.types import DF
        assigned_technician: DF.Link | None
        attachments: DF.AttachImage | None
        body_material: DF.Data | None
        brand: DF.Link | None
        clarinet_type: DF.Literal["B\u266d Soprano", "A Soprano", "E\u266d Soprano", "B\u266d Bass"]
        current_status: DF.Literal["Active", "Needs Repair", "Awaiting Parts", "In Service", "Archived"]
        customer: DF.Link | None
        date_purchased: DF.Date | None
        instrument_type: DF.Literal["B\u266d Clarinet", "A Clarinet", "Bass Clarinet", "E\u266d Clarinet", "Alto Clarinet", "Contrabass Clarinet", "Other"]
        key_plating: DF.Literal["Silver", "Nickel", "Gold", "Other"]
        keywork_plating: DF.Data | None
        last_service_date: DF.Date | None
        model: DF.Data | None
        notes: DF.SmallText | None
        pitch_standard: DF.Data | None
        serial_no: DF.Data
        instrument_category: DF.Link | None
        year_of_manufacture: DF.Int
    # end: auto-generated types
    """Instrument Document Model"""
    def validate(self):
        self.check_duplicate_serial_no()
        self.ensure_valid_instrument_category()

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
