# File: repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Updated: 2025-06-27
# Version: 1.1
# Purpose: Clarinet Intake logic for auto-creating Inspection and enforcing completion
# Notes:
# - Auto-generates Inspection on insert
# - Prevents submit if Inspection is not completed

import frappe
from frappe.model.document import Document

class ClarinetIntake(Document):

    def after_insert(self):
        if not self.inspection_completed:
            insp = frappe.get_doc({
                "doctype": "Clarinet Inspection",
                "intake": self.name,
                "instrument": "Clarinet",
                "status": "Open"
            })
            insp.insert()
            frappe.msgprint(
                f"Inspection {insp.name} auto-created. Please complete it before submitting.",
                alert=True
            )

    def validate(self):
        if self.docstatus == 1 and not self.inspection_completed:
            frappe.throw("You must finish and tick ‘Inspection Completed?’ before you can submit.")