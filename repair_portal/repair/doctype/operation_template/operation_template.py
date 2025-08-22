# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/operation_template/operation_template.py
# Last Updated: 2025-07-29
# Version: v0.1
# Purpose: Controller for Operation Template DocType for managing setup/repair operation blueprints.
# Dependencies: None (standalone single DocType)

from frappe.model.document import Document


class OperationTemplate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        completed: DF.Check
        component_ref: DF.Data | None
        details: DF.SmallText | None
        operation_type: DF.Data
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        section: DF.Data | None
    # end: auto-generated types
    """
    Controller for Operation Template DocType. Stores blueprint for operations, components, and completion status.
    Args:
        Document: Frappe model base class
    Returns:
        None
    """
    pass
