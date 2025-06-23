# File: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-07-10
# Version: 1.4
# Purpose: Auto-generates route for web profile and links to ERPNext

import frappe
from frappe.website.website_generator import WebsiteGenerator


class InstrumentProfile(WebsiteGenerator):
    website = frappe._dict(
        condition_field="published",
        page_title_field="serial_number",
        route="route",
    )

    def validate(self):
        """Ensure route is prefixed with instruments/"""
        if self.serial_number and not self.route:
            self.route = f"instruments/{frappe.scrub(self.serial_number)}"
        elif self.route and not self.route.startswith("instruments/"):
            self.route = f"instruments/{self.route.lstrip('/')}"

    def get_context(self, context):
        context.parents = [{"title": "Instrument Catalog", "route": "/my_instruments"}]
        context.title = self.serial_number
