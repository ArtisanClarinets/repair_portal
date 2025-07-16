# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-14
# Version: v2.0
# Purpose: Handles Clarinet Intake submission logic, including auto-creation of Instrument Profile, Quality Inspection, and Initial Setup for Inventory intakes.
# Dependencies: Instrument Profile, Clarinet Initial Setup, frappe.log_error

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class ClarinetIntake(Document):
    """
    Document controller for Clarinet Intake.
    Automates Instrument Profile and Initial Setup (not Repair Order) creation for Inventory intakes.
    Args:
        Document (frappe.model.document.Document): The standard DocType controller.
    """
    def before_submit(self):
        try:
            if self.intake_type == "Inventory":
                # 1. Instrument Profile
                instr_profile = None
                if not self.instrument_profile:
                    instr_profile = frappe.get_doc({
                        "doctype": "Instrument Profile",
                        "serial_no": self.serial_no,
                        "item_code": self.item_code,
                        "customer": self.customer,
                        "linked_intake": self.name
                    }).insert(ignore_permissions=True)
                    self.instrument_profile = instr_profile.name
                else:
                    instr_profile = frappe.get_doc("Instrument Profile", self.instrument_profile)
                # 2. Clarinet Initial Setup
                setup_doc = frappe.get_doc({
                    "doctype": "Clarinet Initial Setup",
                    "instrument_profile": instr_profile.name,
                    "intake": self.name,
                    "setup_status": "Pending"
                }).insert(ignore_permissions=True)
                self.linked_initial_setup = setup_doc.name
            elif self.intake_type == "Repair":
                # Existing logic for repair intakes (e.g., Repair Order) here
                pass
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Clarinet Intake Automation Error")
            frappe.throw(f"Automation failed: {e}")
