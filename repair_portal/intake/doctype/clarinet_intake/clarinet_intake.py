# relative path: intake/doctype/clarinet_intake/clarinet_intake.py
# updated: 2025-06-18
# version: 1.1
# purpose: On submit, spawn setup entry, validate completion and link instrument profile

import frappe
from frappe.model.document import Document


class ClarinetIntake(Document):
    def validate(self):
        missing = []

        if not self.instrument_profile and self.serial_number:
            existing = frappe.db.exists('Instrument Profile', {'serial_number': self.serial_number})
            if existing:
                self.instrument_profile = existing
            else:
                profile = frappe.new_doc('Instrument Profile')
                profile.serial_number = self.serial_number
                profile.brand = self.brand
                profile.model = self.model
                profile.instrument_category = self.instrument_category
                profile.owner = self.customer
                profile.insert(ignore_permissions=True)
                self.instrument_profile = profile.name

        if not self.instrument_profile:
            missing.append('Instrument Profile')
        if not self.checklist:
            missing.append('Checklist')
        if not self.customer_consent_form:
            missing.append('Consent Form')
        if not self.appointment:
            missing.append('Appointment')
        if missing:
            frappe.throw(f'Cannot submit Intake — missing: {", ".join(missing)}')

    def on_submit(self):
        setup = frappe.new_doc('Clarinet Initial Setup')
        setup.intake = self.name
        setup.instrument_profile = self.instrument_profile
        setup.customer = self.customer
        setup.insert(ignore_permissions=True)
        frappe.msgprint('Initial Setup created and linked.')
