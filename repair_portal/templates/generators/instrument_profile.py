# File: repair_portal/templates/generators/instrument_profile.py
# Updated: 2025-06-14
# Version: 1.0
# Purpose: Defines Instrument Profile web view access and rendering restrictions

import frappe
from frappe.website.page_renderers.template_page import BaseTemplatePage

class InstrumentProfileWebView(BaseTemplatePage):
    def can_access(self):
        return frappe.session.user != "Guest"

    def get_context(self, context):
        doc = self.doc
        context.title = f"Instrument {doc.instrument_name} ({doc.serial_number})"
        context.instrument = doc
        context.parents = [
            {"route": "/instrument-profile", "label": "All Instruments"}
        ]