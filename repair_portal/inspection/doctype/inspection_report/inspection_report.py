# Path: inspection/doctype/inspection_report/inspection_report.py
# Date: 2025-12-15
# Version: 0.1.0
# Description: Server controller for Inspection Report; basic defaults and lightweight validation.
# Dependencies: frappe

import frappe
from frappe import _
from frappe.model.document import Document


class InspectionReport(Document):
    def validate(self):
        # Ensure a sensible default status
        if not getattr(self, "status", None):
            self.status = "Scheduled"

        # Normalize serial_no to empty string when missing
        if not getattr(self, "serial_no", None):
            self.serial_no = ""

        # Ensure instrument_profile exists if provided
        if getattr(self, "instrument_profile", None):
            if not frappe.db.exists("Instrument Profile", self.instrument_profile):
                frappe.throw(_("Instrument Profile {0} not found").format(self.instrument_profile))
