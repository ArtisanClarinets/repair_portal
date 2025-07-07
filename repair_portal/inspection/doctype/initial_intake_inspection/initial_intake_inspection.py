# File Header Template
# Relative Path: repair_portal/inspection/doctype/initial_intake_inspection/initial_intake_inspection.py
# Last Updated: 2025-07-06 (Updated: 2025-07-07 for Clarinet Intake linkage)
# Version: v1.1
# Purpose: Initial Intake Inspection controller for documenting first inspection of clarinets.
# Enforces complete baseline logging, delivery-triggered acclimatization reminder.
# Dependencies: frappe.email, frappe.utils

import frappe
from frappe import _
from frappe.model.document import Document

class InitialIntakeInspection(Document):
    def validate(self):
        """Ensure required fields and compliance with process."""
        if not self.instrument_serial:
            frappe.throw(_("Instrument Serial Number is required."))

        if not self.digital_signature:
            frappe.throw(_("Technician digital signature is required before submission."))

        if not self.rested_unopened:
            frappe.throw(_("You must confirm the instrument rested unopened for at least 4 hours."))

        # Ensure each tone hole has inspection data
        if not self.tone_hole_inspection:
            frappe.throw(_("Please complete the tone hole inspection table."))

        for th in self.tone_hole_inspection:
            if not th.visual_status:
                frappe.throw(_("Tone hole entry is missing Visual Status."))

        # ---- Auto-link Clarinet Intake by serial ----
        if not getattr(self, "clarinet_intake", None) and self.instrument_serial:
            intake_name = frappe.db.get_value(
                "Clarinet Intake",
                {"serial_number": self.instrument_serial},
                "name"
            )
            if intake_name:
                self.clarinet_intake = intake_name

    def on_submit(self):
        """Handle post-submission workflows."""
        if getattr(self, "instrument_delivered", 0):
            try:
                schedule_acclimatization_reminder(self)
                frappe.msgprint(_("6-month service reminder scheduled."))
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Acclimatization Reminder Scheduling Failed")

def schedule_acclimatization_reminder(doc):
    """Create a ToDo reminder 6 months after delivery."""
    reminder_date = frappe.utils.add_months(doc.modified, 6)
    frappe.get_doc({
        "doctype": "ToDo",
        "owner": doc.owner,
        "reference_type": doc.doctype,
        "reference_name": doc.name,
        "date": reminder_date,
        "status": "Open",
        "description": _("6-month bore oiling and service reminder for instrument {0}").format(doc.instrument_serial or "")
    }).insert(ignore_permissions=True)
