# File: repair_portal/instrument_profile/doctype/player_profile/player_profile.py
# Updated: 2025-07-10
# Version: 1.2
# Purpose: WebsiteGenerator for player profiles with prefixed routes.

import frappe
from frappe.website.website_generator import WebsiteGenerator


class PlayerProfile(WebsiteGenerator):
    website = frappe._dict(
        condition_field="published",
        page_title_field="player_name",
        route="route",
    )

    def validate(self):
        """Set default route under /players."""
        if self.player_name and not self.route:
            self.route = f"players/{frappe.scrub(self.player_name)}"
        elif self.route and not self.route.startswith("players/"):
            self.route = f"players/{self.route.lstrip('/')}"

    def get_context(self, context):
        context.title = self.player_name
        context.parents = [{"title": "My Players", "route": "/my_players"}]
