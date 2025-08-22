# relative path: repair_portal/instrument_profile/doctype/client_instrument_profile/client_instrument_profile.py
# updated: 2025-06-15
# version: 1.0.0
# purpose: Server-side logic for Client-Created Instrument Profiles

import frappe
from frappe.model.document import Document


class ClientInstrumentProfile(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from repair_portal.customer.doctype.consent_log_entry.consent_log_entry import (
            ConsentLogEntry,
        )
        from repair_portal.instrument_profile.doctype.customer_external_work_log.customer_external_work_log import (
            CustomerExternalWorkLog,
        )
        from repair_portal.instrument_profile.doctype.instrument_photo.instrument_photo import (
            InstrumentPhoto,
        )

        anonymize_for_research: DF.Check
        condition_images: DF.Table[InstrumentPhoto]
        consent_log: DF.Table[ConsentLogEntry]
        external_work_logs: DF.Table[CustomerExternalWorkLog]
        instrument_category: DF.Literal['Clarinet', 'Bass Clarinet', 'Contrabass Clarinet']
        instrument_model: DF.Data
        instrument_owner: DF.Link
        ownership_transfer_to: DF.Link | None
        purchase_receipt: DF.Attach | None
        repair_preferences: DF.SmallText | None
        serial_no: DF.Link
        technician_notes: DF.Text | None
        verification_status: DF.Literal['Pending', 'Approved', 'Rejected']

    # end: auto-generated types
    def before_save(self):
        if self.verification_status == 'Rejected' and not self.technician_notes:
            frappe.throw('Technician Notes required when rejecting instrument.')

    def on_update(self):
        if self.verification_status == 'Approved':
            frappe.db.set_value(
                'Instrument Profile',
                self.name,
                {
                    'owner': self.owner,
                    'instrument_model': self.instrument_model,
                    'instrument_category': self.instrument_category,
                },
                update_modified=False,
            )
