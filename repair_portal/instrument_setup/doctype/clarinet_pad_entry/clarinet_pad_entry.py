# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/clarinet_pad_entry/clarinet_pad_entry.py
# Last Updated: 2025-07-25
# Version: v1.0
# Purpose: Represents a single pad definition for top/bottom joint pad entries
# Dependencies: None

import frappe
from frappe.model.document import Document

class ClarinetPadEntry(Document):
    """
    Describes a single clarinet pad (position, type, open/closed).
    Used as a child table in Clarinet Pad Map.
    """
    pass