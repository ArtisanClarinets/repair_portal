# relative path: intake/doctype/clarinet_intake/clarinet_intake.py
# updated: 2025-06-26
# version: 1.1
# purpose: On submit, spawn setup entry, validate completion

import frappe
from frappe.model.document import Document


class ClarinetIntake(Document):
    def validate(self):
        missing = []
        if not self.checklist:
            missing.append("Checklist")
        if not self.customer_consent_form:
            missing.append("Consent Form")
        if not self.appointment:
            missing.append("Appointment")
        if missing:
            frappe.throw(f'Cannot submit Intake — missing: {", ".join(missing)}')

        self.sync_checkboxes_to_checklist()

    def on_submit(self):
        setup = frappe.new_doc("Clarinet Initial Setup")
        setup.intake = self.name
        setup.instrument_profile = self.instrument_profile
        setup.customer = self.customer
        setup.insert(ignore_permissions=True)
        frappe.msgprint("Initial Setup created and linked.")

    def sync_checkboxes_to_checklist(self):
        """Ensure boolean damage flags appear in the checklist child table."""
        mapping = {
            "case_damage": "Case Damage",
            "tenon_wear": "Tenon Wear",
            "loose_rods": "Loose Rods",
        }

        existing = {item.check_item for item in (self.checklist or [])}
        for field, label in mapping.items():
            if getattr(self, field, None) and label not in existing:
                self.append("checklist", {"check_item": label, "checked": 1})
