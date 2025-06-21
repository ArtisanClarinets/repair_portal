# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-17
# Version: 1.3
# Purpose: Auto-generates route for web profile and links to ERPNext

import frappe
from frappe.website.website_generator import WebsiteGenerator


class InstrumentProfile(WebsiteGenerator):
    website = frappe._dict(
        condition_field="published",
        page_title_field="serial_number",
        route="route"
    )

    def validate(self):
        # Auto-set route from serial number
        if not self.route and self.serial_number:
            self.route = frappe.scrub(self.serial_number)

    def get_context(self, context):
        context.parents = [{"title": "Instrument Catalog", "route": "/my_instruments"}]
        context.title = self.serial_number