from frappe.website.website_generator import WebsiteGenerator
import frappe

class InstrumentProfile(WebsiteGenerator):
    website = frappe._dict(
        condition_field="published",
        page_title_field="serial_number",
        route="route"
    )

    def get_context(self, context):
        context.parents = [{"title": "Instrument Catalog", "route": "/my_instruments"}]
        context.title = self.serial_number