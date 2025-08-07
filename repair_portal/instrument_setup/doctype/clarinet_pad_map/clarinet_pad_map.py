# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py
# Last Updated: 2025-07-28
# Version: v1.3
# Purpose: Auto-populates pad layout template for French-style clarinets (B♭, A, C, D, E♭) using instrument category; exposes method for client trigger
# Dependencies: Clarinet Pad Entry, Instrument Model, Instrument Category

from __future__ import annotations

import frappe
from frappe.model.document import Document

STANDARD_CLARINET_TYPES = {
    "B♭", "A", "C", "D", "E♭"
}

STANDARD_PAD_NAMES_TOP = [
    "Register Key",
    "C Trill Key",
    "B♭ Trill Key",
    "F# Trill Key",
    "B♭/E♭ Trill Key",
    "A Key",
    "G#/Ab Key",
    "E/B Ring (LH 1)",
    "D/A Ring (LH 2)",
    "C/G Ring (LH 3)",
    "Inline B♭/E♭ Key",
    "C#/G# Key"
]

STANDARD_PAD_NAMES_BOTTOM = [
    "3 Ring Key",
    "Inline F#/B Key",
    "A♭/E♭ Pinky Key",
    "F#/C# Pinky Key",
    "F/C Pinky Key",
    "E/B Pinky Key",
    "E♭/B♭ Pinky Key (optional)"
]

class ClarinetPadMap(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_setup.doctype.clarinet_pad_entry.clarinet_pad_entry import ClarinetPadEntry

        bottom_joint_pads: DF.Table[ClarinetPadEntry]
        clarinet_model: DF.Link | None
        instrument_category: DF.Link | None
        pad_map_title: DF.Data | None
        top_joint_pads: DF.Table[ClarinetPadEntry]
    # end: auto-generated types
    """
    Represents the pad layout template for a given clarinet model, including top and bottom joint pads.
    Auto-populates pads for modern French-style clarinets (B♭, A, C, D, E♭) using instrument category from model.
    """
    def validate(self):
        clarinet_type = self.get_clarinet_type()
        # Only auto-populate if both pad tables are empty and clarinet type matches
        if clarinet_type in STANDARD_CLARINET_TYPES and not self.top_joint_pads and not self.bottom_joint_pads:
            self.populate_standard_pad_names()

    def get_clarinet_type(self):
        """
        Fetch the clarinet type (instrument_category title) from the linked instrument model.
        Returns a string or None.
        """
        model = getattr(self, 'instrument_model', None) or getattr(self, 'clarinet_model', None)
        if model:
            category = frappe.db.get_value("Instrument Model", model, "instrument_category")
            if category:
                title = frappe.db.get_value("Instrument Category", category, "title")
                return title
        return None

    def populate_standard_pad_names(self):
        """
        Auto-populate standard modern French-style pad names for top and bottom joints.
        """
        for name in STANDARD_PAD_NAMES_TOP:
            self.append("top_joint_pads", {"pad_position": name})
        for name in STANDARD_PAD_NAMES_BOTTOM:
            self.append("bottom_joint_pads", {"pad_position": name})

    
# ---
# Whitelisted method for client-side JS to trigger auto-population

@frappe.whitelist(allow_guest=False)
def populate_standard_pad_names(docname: str):
    """
    Whitelisted endpoint to populate standard pads from client-side JS.
    Args:
        docname (str): Name of the Clarinet Pad Map doc
    """
    doc = frappe.get_doc("Clarinet Pad Map", docname)
    doc.populate_standard_pad_names() # type: ignore
    doc.save()
    return True
