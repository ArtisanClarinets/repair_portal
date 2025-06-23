# relative path: intake/doctype/clarinet_intake/clarinet_intake.py
# updated: 2025-06-15
# version: 1.0
# purpose: On submit, spawn setup entry, validate completion

import frappe
from frappe.model.document import Document


class ClarinetIntake(Document):
    def validate(self):
        missing = []
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
