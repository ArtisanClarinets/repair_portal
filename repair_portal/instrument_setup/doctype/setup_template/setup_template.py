# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/setup_template/setup_template.py
# Last Updated: 2025-07-25
# Version: v1.0
# Purpose: Auto-create Clarinet Pad Map on Setup Template save
# Dependencies: Clarinet Pad Map

import frappe
from frappe.model.document import Document


class SetupTemplate(Document):
    def validate(self):
        if not self.pad_map:
            pad_map = frappe.get_doc({
                "doctype": "Clarinet Pad Map",
                "clarinet_model": self.clarinet_model
            })
            pad_map.insert(ignore_permissions=True)
            self.pad_map = pad_map.name
            frappe.msgprint(f"Auto-created pad map: {pad_map.name}")