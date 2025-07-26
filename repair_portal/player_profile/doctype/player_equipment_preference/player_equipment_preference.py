# File Header Template
# Relative Path: repair_portal/player_profile/doctype/player_equipment_preference/player_equipment_preference.py
# Last Updated: 2025-07-25
# Version: v1.0
# Purpose: Controller for the Player Equipment Preference child table, capturing all equipment choices in one child table for simplified player profiling.
# Dependencies: Instrument Profile (Doctype)

from frappe.model.document import Document


class PlayerEquipmentPreference(Document):
    """
    Player Equipment Preference child table controller.
    All preferences for mouthpiece, ligature, reed, barrel, and instrument for each player instance.
    """
    pass
