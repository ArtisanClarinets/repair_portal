# relative path: repair_portal/client_profile/doctype/client_profile/client_profile.py
# updated: 2025-06-28
# version: 1.1.0
# purpose: Adds autoname logic and preserves validation of linked user uniqueness

import frappe
from frappe.model.document import Document

class ClientProfile(Document):
    def autoname(self):
        """
        Auto-generate Client Profile ID as CP-000001
        """
        last = frappe.db.sql(
            "select max(cast(substr(client_profile_id, 4) as unsigned)) from `tabClient Profile`"
        )
        next_number = (last[0][0] or 0) + 1
        self.client_profile_id = "CP-" + str(next_number).zfill(6)

    def validate(self):
        self.ensure_unique_user()

    def ensure_unique_user(self):
        if self.linked_user:
            exists = frappe.db.exists("Client Profile", {
                "linked_user": self.linked_user,
                "name": ["!=", self.name]
            })
            if exists:
                frappe.throw(
                    f"This User is already linked to another Client Profile: {exists}"
                )