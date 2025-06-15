# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-15
# Version: 1.1
# Purpose: Server-side logic for Instrument Profile Doctype. Ensures serial uniqueness and updates last_service_date from logs.
# Notes: Tightly integrates with Service Log in repair_logging module for all service event linkage.

import frappe
from frappe.model.document import Document


class InstrumentProfile(Document):
    def validate(self):
        if not self.customer:
            frappe.throw("Customer is required")
        # Ensure unique serial number
        if frappe.db.exists(
            "Instrument Profile", {"serial_number": self.serial_number, "name": ["!=", self.name]}
        ):
            frappe.throw("Serial number must be unique.")

    def update_last_service_date(self):
        # Auto-update last_service_date based on latest service_log
        last_service = frappe.db.sql(
            """
            SELECT MAX(date) FROM `tabService Log` WHERE instrument_profile=%s
        """,
            (self.name,),
            as_list=1,
        )
        if last_service and last_service[0][0]:
            self.last_service_date = last_service[0][0]

    def on_update(self):
        self.update_last_service_date()

    def on_submit(self):
        self.update_last_service_date()
        frappe.msgprint("Instrument Profile submitted and service history synchronized.")
