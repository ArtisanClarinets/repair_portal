# File: repair_portal/intake/doctype/appointment/appointment.py
# Date Updated: 2025-06-12
# Version: v1.0
# Purpose: Server-side controller for Appointment DocType

import frappe
from frappe.model.document import Document


class Appointment(Document):
    def validate(self):
        if self.confirmed and not self.appointment_date:
            frappe.throw('Confirmed appointments must have an appointment date.')
