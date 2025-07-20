# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake_settings/clarinet_intake_settings.py
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Backend controller for Clarinet Intake Settings. Handles field validation,
# JSON parsing for brand mapping, and provides a utility for all business logic to fetch settings.
# Dependencies: frappe (v15)

import frappe
from frappe.model.document import Document
from frappe import _
import json

class ClarinetIntakeSettings(Document):
    """Settings DocType controller for Intake automation."""

    def validate(self):
        # Ensure Brand Mapping is valid JSON
        if self.brand_mapping:
            try:
                json.loads(self.brand_mapping)
            except Exception:
                frappe.throw(_("Brand Mapping Rules must be valid JSON!"))

# Utility to fetch all settings as a dict for business logic

def get_intake_settings():
    """Returns Clarinet Intake Settings as a dict."""
    return frappe.get_single("Clarinet Intake Settings").as_dict()
