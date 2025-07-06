# File: repair_portal/inspection/doctype/clarinet_inspection/clarinet_inspection.py
# Last Updated: 2025-07-05
# Version: v1.1
# Purpose: Stand-alone Clarinet Inspection document for Artisan Clarinets; ensures linkage to Clarinet Intake for traceability
# Dependencies: Inspection Finding, Clarinet Intake

import frappe
from frappe.model.document import Document

class ClarinetInspection(Document):
    """
    Stand-alone inspection document for clarinet setup and repair. Must always link to Clarinet Intake.
    """
    def validate(self):
        if not self.clarinet_intake:
            frappe.log_error(f"Clarinet Inspection {self.name} missing clarinet_intake link.", "Validation Error")
            frappe.throw("This inspection must be linked to a Clarinet Intake.")
