# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/clarinet_pad_entry/clarinet_pad_entry.py
# Last Updated: 2025-07-25
# Version: v1.0
# Purpose: Represents a single pad definition for top/bottom joint pad entries
# Dependencies: None

from frappe.model.document import Document


class ClarinetPadEntry(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        is_open_key: DF.Check
        is_secondary_pad: DF.Check
        pad_position: DF.Data | None
        pad_type: DF.Data | None
        parent: DF.Data
        parent_pad: DF.Link | None
        parentfield: DF.Data
        parenttype: DF.Data
    # end: auto-generated types
    """
    Describes a single clarinet pad (position, type, open/closed).
    Used as a child table in Clarinet Pad Map.
    """
    pass
