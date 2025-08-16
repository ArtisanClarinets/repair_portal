# File Header Template
# Relative Path: repair_portal/player_profile/doctype/player_equipment_preference/player_equipment_preference.py
# Last Updated: 2025-07-25
# Version: v1.0
# Purpose: Controller for the Player Equipment Preference child table, capturing all equipment choices in one child table for simplified player profiling.
# Dependencies: Instrument Profile (Doctype)

from frappe.model.document import Document


class PlayerEquipmentPreference(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        barrel: DF.Data | None
        comments: DF.SmallText | None
        instrument: DF.Link | None
        ligature: DF.Data | None
        mouthpiece: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        reed_brand: DF.Data | None
        reed_model: DF.Data | None
        reed_strength: DF.Data | None
    # end: auto-generated types
    """
    Player Equipment Preference child table controller.
    All preferences for mouthpiece, ligature, reed, barrel, and instrument for each player instance.
    """
    pass
