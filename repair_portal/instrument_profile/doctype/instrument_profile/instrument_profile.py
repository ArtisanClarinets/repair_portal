# Relative Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Last Updated: 2025-07-04
# Version: v2.1
# Purpose: Consolidated server-side logic for Instrument Profile (client + technician workflows)
# Dependencies: Customer, Consent Log Entry, Customer External Work Log

import frappe
from frappe.model.document import Document

class InstrumentProfile(Document):
    serial_number = None  # Ensure attribute exists
    status = None  # Ensure attribute exists
    verification_status = None  # Ensure attribute exists
    technician_notes = None  # Ensure attribute exists

    def validate(self):
        if not self.serial_number:
            frappe.throw("Serial Number is required.")

        if not self.status:
            frappe.throw("Status is required.")

        existing = frappe.db.exists(
            "Instrument Profile",
            {"serial_number": self.serial_number, "name": ["!=", self.name]}
        )
        if existing:
            frappe.throw(f"An Instrument Profile with Serial Number '{self.serial_number}' already exists.")

    def before_save(self):
        if self.verification_status == "Rejected" and not self.technician_notes:
            frappe.throw("Technician Notes are required when rejecting instrument.")

    def on_update(self):
        if not self.qr_code:
            self.qr_code = frappe.generate_hash(length=12)
        frappe.db.set_value(
            "Clarinet Intake",
            {"instrument_profile": self.name},
            "stock_status",
            self.status
        )