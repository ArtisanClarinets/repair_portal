# Path: repair_portal/instrument_profile/doctype/instrument_photo/instrument_photo.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Child table for instrument photos with categorization; auto-sets timestamp and uploaded_by
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
