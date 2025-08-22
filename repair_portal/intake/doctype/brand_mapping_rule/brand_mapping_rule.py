# File Header Template
# Relative Path: repair_portal/intake/doctype/brand_mapping_rule/brand_mapping_rule.py
# Last Updated: 2025-08-16
# Version: v1.1
# Purpose: Define brand mapping rules for instrument profiles in the Repair Portal, ensuring consistency of brand naming.
# Dependencies: Frappe Framework (Document API, frappe.db.exists)

import frappe
from frappe.model.document import Document


class BrandMappingRule(Document):
    """
    Controller for managing brand mapping rules.
    This document defines how external brand names (from_brand) map to standardized brand names (to_brand).
    """

    def validate(self):
        """Ensure brand mapping rules are valid."""
        if not self.from_brand:  # type: ignore
            frappe.throw('From Brand is required')

        if not self.to_brand:  # type: ignore
            frappe.throw('To Brand is required')

        # Prevent duplicate or conflicting rules
        self.validate_unique_mapping()

    def validate_unique_mapping(self):
        """Ensure that the (from_brand, to_brand) mapping is unique."""
        if frappe.db.exists(
            'Brand Mapping Rule',
            {'from_brand': self.from_brand, 'to_brand': self.to_brand, 'name': ['!=', self.name]},  # type: ignore
        ):
            frappe.throw(f"A mapping from '{self.from_brand}' to '{self.to_brand}' already exists.")  # type: ignore
