# Relative Path: repair_portal/player_profile/doctype/player_profile/player_profile.py
# Last Updated: 2025-07-13
# Version: v1.4
# Purpose: WebsiteGenerator for Player Profile with COPPA checks, visibility logic, and route formatting
# Dependencies: Client Profile

import frappe
from frappe.website.website_generator import WebsiteGenerator
from datetime import datetime

class PlayerProfile(WebsiteGenerator):
    website = frappe._dict(condition_field="published", page_title_field="player_name", route="route")

    def autoname(self):
        if not self.route and self.player_name and self.client_profile:
            scrubbed_name = frappe.scrub(self.player_name)
            self.route = f"players/{self.client_profile}-{scrubbed_name}"

    def validate(self):
        if not self.client_profile:
            frappe.throw("Player Profile must be linked to a Client Profile.")

        if self.date_of_birth:
            try:
                age = (datetime.now().date() - self.date_of_birth).days // 365
                if age < 13:
                    self.block_marketing_emails()
            except Exception:
                frappe.log_error(frappe.get_traceback(), "PlayerProfile.validate failed on DOB")

    def block_marketing_emails(self):
        try:
            frappe.db.set_value("Email Group Member", {"email": self.email}, "unsubscribed", 1)
        except Exception:
            pass

    def has_website_permission(self, context):
        client_user = frappe.db.get_value("Client Profile", self.client_profile, "linked_user")
        return frappe.session.user == client_user

    def get_context(self, context):
        context.title = self.player_name or "Player Profile"
        context.parents = [{"title": "My Players", "route": "/dashboard"}]
        context.profile = self.as_dict()