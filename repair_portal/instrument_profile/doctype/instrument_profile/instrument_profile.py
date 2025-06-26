# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-27
# Version: 1.4
# Purpose: Auto-generates route for web profile and links to ERPNext
#          Sanitizes private fields when rendering published profiles.

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

    PRIVATE_FIELDS = [
        "owner",
        "client_profile",
        "wellness_score",
        "clarinet_pad_map",
        "qr_code_svg",
    ]

    def get_context(self, context):
        context.parents = [{"title": "Instrument Catalog", "route": "/my_instruments"}]
        context.title = self.serial_number
        if self.published:
            sanitized = self.as_dict()
            for field in self.PRIVATE_FIELDS:
                sanitized.pop(field, None)
            context.profile = sanitized
        return context
