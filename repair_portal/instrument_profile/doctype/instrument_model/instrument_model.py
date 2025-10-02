# Path: repair_portal/instrument_profile/doctype/instrument_model/instrument_model.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Master data for instrument models (Brand + Model + Category + Body Material); validates uniqueness
# Dependencies: frappe, Brand, Instrument Category

from frappe.model.document import Document


class InstrumentModel(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        body_material: DF.Data
        brand: DF.Link
        instrument_category: DF.Link
        instrument_model_id: DF.Data | None
        model: DF.Data
    # end: auto-generated types
    pass
