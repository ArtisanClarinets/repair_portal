# File relative path: repair_portal/intake/doctype/brand_mapping_rule/brand_mapping_rule.py
# Updated: 2025-07-19
# Version: 1.0
# Purpose: Define brand mapping rules for instrument profiles in the Repair Portal


import frappe
from frappe.model.document import Document


class BrandMappingRule(Document):
    """
    Controller for managing brand mapping rules.
    This document defines how brands are mapped to instrument profiles.
    """

    def validate(self):
        """Ensure brand mapping rules are valid."""
        if not self.brand_name:
            frappe.throw("Brand Name is required")

        if not self.instrument_category:
            frappe.throw("Instrument Category is required")

        # Additional validation logic can be added here
        self.validate_unique_mapping()

    def validate_unique_mapping(self):
        """Ensure that the brand mapping is unique."""
        if frappe.db.exists("Brand Mapping Rule", {"brand_name": self.brand_name, "instrument_category": self.instrument_category}):
            frappe.throw("This brand mapping already exists.")