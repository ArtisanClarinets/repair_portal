# Path: repair_portal/instrument_profile/doctype/instrument_category/instrument_category.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Master data for instrument categories (e.g., Bb Clarinet, Bass Clarinet); validates uniqueness and active status
# Dependencies: frappe

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
