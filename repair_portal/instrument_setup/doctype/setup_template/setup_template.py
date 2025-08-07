# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/setup_template/setup_template.py
# Last Updated: 2025-07-25
# Version: v1.0
# Purpose: Auto-create Clarinet Pad Map on Setup Template save
# Dependencies: Clarinet Pad Map

import frappe
from frappe.model.document import Document


class SetupTemplate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_setup.doctype.clarinet_setup_operation.clarinet_setup_operation import ClarinetSetupOperation
        from repair_portal.instrument_setup.doctype.setup_checklist_item.setup_checklist_item import SetupChecklistItem

        checklist_items: DF.Table[SetupChecklistItem]
        clarinet_model: DF.Link
        default_operations: DF.Table[ClarinetSetupOperation]
        pad_map: DF.Link | None
        template_name: DF.Data | None
    # end: auto-generated types
    def validate(self):
        if not self.pad_map:
            pad_map = frappe.get_doc({
                "doctype": "Clarinet Pad Map",
                "clarinet_model": self.clarinet_model
            })
            pad_map.insert(ignore_permissions=True)
            self.pad_map = pad_map.name
            frappe.msgprint(f"Auto-created pad map: {pad_map.name}")