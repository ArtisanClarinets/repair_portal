# repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-06-15
# Version: 1.4
# Purpose: Warranty logic including manual modification tracking + logging

import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime

class InstrumentProfile(Document):
    def validate(self):
        if self.warranty_start_date and self.warranty_end_date:
            self.warranty_active = self.warranty_start_date <= today() <= self.warranty_end_date

    def before_save(self):
        if self.has_value_changed("warranty_start_date") or self.has_value_changed("warranty_end_date"):
            if not self.warranty_modification_reason:
                frappe.throw("Please provide a reason for modifying the warranty period.")

            frappe.get_doc({
                "doctype": "Warranty Modification Log",
                "instrument_profile": self.name,
                "modified_by": frappe.session.user,
                "modification_date": now_datetime(),
                "old_start_date": self.get_db_value("warranty_start_date"),
                "new_start_date": self.warranty_start_date,
                "old_end_date": self.get_db_value("warranty_end_date"),
                "new_end_date": self.warranty_end_date,
                "reason": self.warranty_modification_reason
            }).insert(ignore_permissions=True)

            frappe.msgprint(f"Warranty updated and logged for instrument {self.name}.")