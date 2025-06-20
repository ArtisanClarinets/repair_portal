# File: repair_portal/instrument_profile/doctype/ownership_transfer/ownership_transfer.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Handles secure transfer of instrument ownership with user verification and approval

import frappe
from frappe.model.document import Document

class OwnershipTransfer(Document):
    def validate(self):
        if self.from_user == self.to_user:
            frappe.throw("Cannot transfer ownership to the same user.")

    def on_submit(self):
        if not self.approved:
            frappe.throw("Ownership transfer must be approved before submission.")

        instrument = frappe.get_doc("Instrument", self.instrument)
        instrument.owner = self.to_user
        instrument.save(ignore_permissions=True)
        frappe.msgprint("Ownership has been successfully transferred.")