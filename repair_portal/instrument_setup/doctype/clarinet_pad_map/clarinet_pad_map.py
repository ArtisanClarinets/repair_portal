# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py
# Last Updated: 2025-07-25
# Version: v1.0
# Purpose: Defines the pad layout template per clarinet model for fingering and configuration
# Dependencies: Clarinet Pad Entry

from frappe.model.document import Document


class ClarinetPadMap(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_setup.doctype.clarinet_pad_entry.clarinet_pad_entry import ClarinetPadEntry

        bottom_joint_pads: DF.Table[ClarinetPadEntry]
        clarinet_model: DF.Data | None
        top_joint_pads: DF.Table[ClarinetPadEntry]
    # end: auto-generated types
    """
    Represents the pad layout template for a given clarinet model, including top and bottom joint pads.
    """
    pass