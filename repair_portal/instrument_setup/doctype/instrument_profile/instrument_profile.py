"""
Relative Path: repair_portal/instrument_setup/doctype/instrument_profile/instrument_profile.py
Last Updated: 2025-06-13
Version: 1.0
Purpose: Server-side controller for the Instrument Profile DocType
"""

import frappe
from frappe.model.document import Document

class InstrumentProfile(Document):
    """Lightweight controller for Instrument Profile."""

    #: configuration for Frappe website rendering
    website = frappe._dict(
        condition_field="name",
        page_title_field="serial_number",
    )
