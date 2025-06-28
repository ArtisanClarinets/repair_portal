# File: repair_portal/player_profile/doctype/player_profile/player_profile.py
# Updated: 2025-06-28
# Version: 1.1.0
# Purpose: WebsiteGenerator controller for Player Profile with context rendering

import frappe
from frappe.website.website_generator import WebsiteGenerator

class PlayerProfile(WebsiteGenerator):
    website = frappe._dict(
        condition_field="published",
        page_title_field="player_name",
        route="route"
    )

    def get_context(self, context):
        context.title = self.player_name
        context.parents = [{"title": "My Players", "route": "/dashboard"}]
        context.profile = self.as_dict()