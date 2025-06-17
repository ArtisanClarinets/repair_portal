# relative path: repair_portal/client_profile/doctype/client_profile/client_profile.py
# updated: 2025-06-16
# version: 1.0.0
# purpose: Controller logic for Client Profile including validation, link-checking

import frappe
from frappe.model.document import Document

class ClientProfile(Document):
    def validate(self):
        self.ensure_unique_user()

    def ensure_unique_user(self):
        if self.linked_user:
            exists = frappe.db.exists("Client Profile", {
                "linked_user": self.linked_user,
                "name": ["!=", self.name]
            })
            if exists:
                frappe.throw(f"This User is already linked to another Client Profile: {exists}")