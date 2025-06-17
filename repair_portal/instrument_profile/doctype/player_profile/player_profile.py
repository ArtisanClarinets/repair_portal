from frappe.website.website_generator import WebsiteGenerator
import frappe

class PlayerProfile(WebsiteGenerator):
    website = frappe._dict(
        condition_field="published",
        page_title_field="player_name",
        route="route"
    )

    def get_context(self, context):
        context.title = self.player_name
        context.parents = [{"title": "My Players", "route": "/dashboard"}]