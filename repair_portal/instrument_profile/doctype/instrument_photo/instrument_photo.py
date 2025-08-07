# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument_photo/instrument_photo.py
# Last Updated: 2025-07-23
# Version: v1.0
# Purpose: Child table to store all photo/image records linked to an instrument's lifecycle (hero/profile, marketing, service, etc.)
# Dependencies: frappe, User

from frappe.model.document import Document


class InstrumentPhoto(Document):
    """
    Controller for Instrument Photo child table.
    Used for photo attachments on Instrument, Inspection, and Profile doctypes.
    """
    pass
