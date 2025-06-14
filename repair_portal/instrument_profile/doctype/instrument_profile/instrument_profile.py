# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-14
# Version: 1.1
# Purpose: Controller logic for Instrument Profile Doctype with web rendering support

import frappe
from frappe.website.website_generator import WebsiteGenerator

class InstrumentProfile(WebsiteGenerator):
    """Server side logic for the Instrument Profile DocType with website rendering support."""

    website = frappe._dict(
        condition_field="published",
        page_title_field="serial_number",
    )

    def validate(self):
        if self.acquisition_type == "Customer" and not self.customer:
            frappe.throw("Customer is required for customer-owned instruments.")

    def on_submit(self):
        frappe.msgprint("Instrument profile submitted successfully.")
