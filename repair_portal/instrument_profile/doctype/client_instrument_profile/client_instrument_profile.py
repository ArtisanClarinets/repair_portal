# relative path: repair_portal/instrument_profile/doctype/client_instrument_profile/client_instrument_profile.py
# updated: 2025-06-15
# version: 1.0.0
# purpose: Server-side logic for Client-Created Instrument Profiles

import frappe
from frappe.model.document import Document


class ClientInstrumentProfile(Document):
    def before_save(self):
        if self.verification_status == "Rejected" and not self.technician_notes:
            frappe.throw("Technician Notes required when rejecting instrument.")

    def on_update(self):
        if self.verification_status == "Approved":
            frappe.db.set_value(
                "Instrument Profile",
                self.name,
                {
                    "owner": self.owner,
                    "instrument_model": self.instrument_model,
                    "instrument_category": self.instrument_category,
                },
                update_modified=False,
            )