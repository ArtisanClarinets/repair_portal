# File: repair_portal/lab/doctype/intonation_session/intonation_session.py
# Updated: 2025-06-17
# Version: 1.0
# Purpose: Parent DocType for smart intonation sessions.

"""Parent DocType for smart intonation sessions."""

from frappe.model.document import Document


class IntonationSession(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.lab.doctype.intonation_note.intonation_note import IntonationNote

        code: DF.Code | None
        customer: DF.Link
        instrument: DF.Link | None
        json_data: DF.LongText | None
        notes: DF.Table[IntonationNote]
        player: DF.Link | None
        plot_attachment: DF.AttachImage | None
        repair_order: DF.Link | None
        session_type: DF.Literal["Pre-Repair", "Post-Repair", "Standalone"]
    # end: auto-generated types
    pass
