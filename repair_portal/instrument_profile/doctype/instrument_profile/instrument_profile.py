# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-14
# Version: 2.0
# Purpose: Enhanced Instrument Profile logic with website context, validation, and traceability

import frappe
from frappe.website.website_generator import WebsiteGenerator

class InstrumentProfile(WebsiteGenerator):
    """Enhanced Instrument Profile with full web context and lifecycle logic."""

    website = frappe._dict(
        condition_field="published",
        page_title_field="serial_number",
    )

    def validate(self):
        if self.acquisition_type == "Customer" and not self.customer:
            frappe.throw("Customer is required for customer-owned instruments.")

        # Auto-status update if condition logs are added
        if self.status == "Active" and self.condition_records:
            self.status = "In Repair"

    def on_submit(self):
        frappe.msgprint("Instrument profile submitted successfully.")

    def get_context(self, context):
        # Web context rendering with linked logs
        context.instrument = self
        context.setups = frappe.get_all("Clarinet Initial Setup", fields=["setup_date", "technician", "status"], filters={"instrument_profile": self.name})
        context.conditions = frappe.get_all("Instrument Condition Record", fields=["date", "technician", "condition_notes"], filters={"parent": self.name})
        context.page_title = f"Instrument {self.serial_number} ({self.instrument_type})"
        return context