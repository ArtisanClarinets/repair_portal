# File: repair_portal/repair_portal/instrument_setup/doctype/setup_checklist_item/setup_checklist_item.py
# Updated: 2025-06-12
# Version: 1.1
# Purpose: Setup Checklist Item for technician task tracking in Clarinet Initial Setup

from frappe.model.document import Document


class SetupChecklistItem(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        completed: DF.Check
        notes: DF.Text | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        task: DF.Data | None
    # end: auto-generated types
    pass
