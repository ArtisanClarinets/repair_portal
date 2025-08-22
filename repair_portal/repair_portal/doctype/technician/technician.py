# File Header Template
# Relative Path: repair_portal/doctype/technician/technician.py
# Last Updated: 2025-07-17
# Version: v1.0
# Purpose: Technician master data, onboarding, and activity audit logic.
# Dependencies: User, Technician Certification
from __future__ import annotations
import frappe
from frappe.model.document import Document
from frappe.utils import now


class Technician(Document):
    """
    Technician Doctype Controller
    Handles audit, onboarding notification, and activity tracking for repair technicians.
    """

    def before_save(self):
        try:
            self.validate_email()
            self.validate_phone()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), 'Technician.before_save')
            frappe.throw(f'Technician validation failed: {e}')

    def after_insert(self):
        try:
            self.send_onboarding_email()
        except Exception:
            frappe.log_error(frappe.get_traceback(), 'Technician.after_insert')

    def validate_email(self):
        if self.email and '@' not in self.email:  # type: ignore
            frappe.throw('Please enter a valid email address.')

    def validate_phone(self):
        digits = [c for c in (self.phone or '') if c.isdigit()]  # type: ignore
        if len(digits) < 10:
            frappe.throw('Please enter a valid phone number.')

    def send_onboarding_email(self):
        if self.user and self.email:  # type: ignore
            frappe.sendmail(
                recipients=[self.email],  # type: ignore
                subject='Welcome to the Repair Portal!',
                message=f"Dear {self.first_name},<br><br>Welcome to the team! Your user account is: <b>{self.user}</b>.<br><br>Login at: <a href='https://erp.artisanclarinets.com'>erp.artisanclarinets.com</a>",  # type: ignore
            )

    def on_update(self):
        self.last_active = now()
