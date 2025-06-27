# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-27
# Version: 1.6
# Purpose: Adds validation that enforces workflow integrity during profile setup.

import frappe
from frappe.website.website_generator import WebsiteGenerator


class InstrumentProfile(WebsiteGenerator):
    website = frappe._dict(condition_field="published", page_title_field="serial_number", route="route")

    def validate(self):
        # Auto-set route from serial number
        if not self.route and self.serial_number:
            self.route = frappe.scrub(self.serial_number)

        # Ensure linked profiles before state transitions
        if self.profile_status == "Ready for Use":
            if not self.client_profile:
                frappe.throw("Client Profile must be set before this instrument can be marked Ready for Use.")
            if not self.player_profile:
                frappe.throw("Player Profile must be set before this instrument can be marked Ready for Use.")

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
