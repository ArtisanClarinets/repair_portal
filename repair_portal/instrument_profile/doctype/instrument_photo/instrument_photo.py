# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument_photo/instrument_photo.py
# Last Updated: 2025-07-23
# Version: v1.0
# Purpose: Child table to store all photo/image records linked to an instrument's lifecycle (hero/profile, marketing, service, etc.)
# Dependencies: frappe, User

from frappe.model.document import Document


class InstrumentPhoto(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        category: DF.Literal[
            'Profile Picture',
            'Service Before',
            'Service After',
            'Damage Documentation',
            'Repair Documentation',
            'Other',
        ]
        description: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        photo: DF.AttachImage
        timestamp: DF.Datetime | None
        uploaded_by: DF.Link
    # end: auto-generated types
    """
    Controller for Instrument Photo child table.
    Used for photo attachments on Instrument, Inspection, and Profile doctypes.
    """
    pass
