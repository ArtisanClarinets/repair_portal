# File: repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-28
# Version: 1.7
# Purpose: Adds validation for workflow integrity and auto-generates a unique identifier.

import frappe
import random
import string
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

        # Auto-generate unique identifier if missing
        if not self.unique_identifier:
            self.generate_unique_identifier()

        # Ensure linked profiles before state transitions
        if self.profile_status == "Ready for Use":
            if not self.client_profile:
                frappe.throw("Client Profile must be set before this instrument can be marked Ready for Use.")
            if not self.player_profile:
                frappe.throw("Player Profile must be set before this instrument can be marked Ready for Use.")

    def generate_unique_identifier(self):
        """
        Generates a unique identifier in the format: INSTR-######.
        """
        unique_id = "INSTR-" + self.random_string(6)
        self.unique_identifier = unique_id

    def random_string(self, length=6):
        """
        Generate a random string of digits.
        """
        digits = string.digits
        return ''.join(random.choice(digits) for _ in range(length))

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