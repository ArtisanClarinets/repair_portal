# File Header Template
# Relative Path: repair_portal/repair_logging/doctype/tenon_fit_record/tenon_fit_record.py
# Last Updated: 2025-07-06
# Version: v1.0
# Purpose: Child table to record fit assessments for each clarinet tenon.
# Dependencies: frappe

import frappe
from frappe import _
from frappe.model.document import Document

class TenonFitRecord(Document):
    def validate(self):
        """Ensure each entry has classification and at least one note or measurement."""
        if not self.fit_classification:
            frappe.throw(_("Fit Classification is required (Loose, Ideal, or Tight)."))
        
        if not self.joint:
            frappe.throw(_("Joint selection is required."))

        if not self.notes and not self.measured_diameter:
            frappe.throw(_("Please enter a note or measured diameter for Tenon Fit Record."))
