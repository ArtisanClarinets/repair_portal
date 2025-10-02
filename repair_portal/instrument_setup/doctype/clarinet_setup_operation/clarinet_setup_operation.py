# File: repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_operation/clarinet_setup_operation.py
# Updated: 2025-06-12
# Version: 1.1
# Purpose: Clarinet Setup Operation (Child Table) — tracks manual service tasks by section and type

from frappe.model.document import Document


class ClarinetSetupOperation(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        completed: DF.Check
        component_ref: DF.Data | None
        details: DF.Text | None
        operation_type: DF.Data  # Select field with operation options
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        section: DF.Data  # Select field with section options: All, Mouthpiece, etc.
    # end: auto-generated types
    pass
