# ---------------------------------------------------------------------------
# File: repair_portal/player_profile/doctype/player_profile/player_profile.py
# Updated: 2025-06-29
# Version: 1.3.0
# Purpose: WebsiteGenerator for Player Profile with route and permission logic
# ---------------------------------------------------------------------------

import frappe
from frappe.website.website_generator import WebsiteGenerator


class PlayerProfile(WebsiteGenerator):
    website = frappe._dict(condition_field="published", page_title_field="player_name", route="route")

    def autoname(self):
        """Auto-generate route only on creation if not set."""
        if not self.route and self.player_name and self.client_profile:
            scrubbed_name = frappe.scrub(self.player_name)
            self.route = f"players/{self.client_profile}-{scrubbed_name}"

    def validate(self):
        """Enforce client linkage."""
        if not self.client_profile:
            frappe.throw("Player Profile must be linked to a Client Profile.")

    def has_website_permission(self, context):
        """Restrict visibility to the linked user."""
        client_user = frappe.db.get_value("Client Profile", self.client_profile, "linked_user")
        return frappe.session.user == client_user

    def get_context(self, context):
        """Provide page rendering context."""
        context.title = self.player_name or "Player Profile"
        context.parents = [{"title": "My Players", "route": "/dashboard"}]
        context.profile = self.as_dict()
