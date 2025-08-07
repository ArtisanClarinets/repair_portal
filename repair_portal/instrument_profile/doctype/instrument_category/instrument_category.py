# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument_category/instrument_category.py
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Minimal controller for Instrument Category DocType (used as category master for instruments).
# Dependencies: None

from frappe.model.document import Document


class InstrumentCategory(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        description: DF.SmallText | None
        is_active: DF.Check
        title: DF.Data
    # end: auto-generated types
    """
    Minimal DocType controller for Instrument Category.
    No custom business logic yet.
    """
    pass
