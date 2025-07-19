# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-19
# Version: v2.2
# Purpose: Single-source controller for all Clarinet Intake logic, including event blocking, inventory/repair/maintenance rules, audit logging, and automatic Instrument Inspection creation.
# Dependencies: frappe

from __future__ import annotations

import logging

import frappe
from frappe import _
from frappe.model.document import Document

LOG = frappe.logger("repair_portal.intake", allow_site=True)
LOG.setLevel(logging.INFO)


def _err(msg: str, title: str) -> None:
    """Log + create an Error Log entry that is visible in the Desk."""
    LOG.error(msg)
    frappe.log_error(msg, title)


class ClarinetIntake(Document):
    """
    All-in-one controller for Clarinet Intake. Handles business rules, blocking edits for flagged intakes, robust audit logging, and automatic Instrument Inspection creation.
    """
    
    def validate(self) -> None:
        """
        Require customer for Repair intake type only.
        """
        if self.intake_type == "Repair" and not self.customer:
            frappe.throw(_("Customer is required for Repair Intake."), frappe.ValidationError)

    def before_save(self) -> None:
        """
        Runs before saving any Clarinet Intake. Delegates to intake-type handlers and triggers Instrument Inspection creation.
        """
        if self.intake_status == "Flagged":
            _err(f"Edit blocked on flagged intake {self.name}", "Flagged Intake Edit")
            frappe.throw(_("Editing is not allowed while intake is Flagged."))
        if self.intake_type not in ["Inventory", "Repair", "Maintenance"]:
            frappe.throw(_("Intake type must be Inventory, Maintenance, or Repair."))

        # Ensure linked Instrument Inspection exists (auto-create if missing)
        self.create_instrument_inspection()

    def create_instrument_inspection(self) -> None:
        """
        Automatically creates a linked Instrument Inspection if one doesn't already exist for this Clarinet Intake.
        """
        try:
            if not self.serial_no:
                # No serial number to link inspection, skip
                return
            inspection_exists = frappe.db.exists("Instrument Inspection", {"clarinet_intake": self.name})
            if not inspection_exists:
                inspection_doc = frappe.get_doc(
                    {
                        "doctype": "Instrument Inspection",
                        "inspection_date": frappe.utils.nowdate(),
                        "inspection_type": (
                            self.intake_type
                            if self.intake_type in ["Repair", "Maintenance"]
                            else "New Inventory"
                        ),
                        "serial_no": self.serial_no,
                        "clarinet_intake": self.name,
                        # 'inspected_by' is required, but must be set by technician; leave blank here
                    }
                )
                inspection_doc.insert(ignore_permissions=True)
                frappe.msgprint(_("Instrument Inspection created and linked to Intake."))
        except Exception:
            frappe.log_error(frappe.get_traceback(), "ClarinetIntake.create_instrument_inspection")

    def before_cancel(self) -> None:
        """
        Block cancel if intake is flagged.
        """
        if self.intake_status == "Flagged":
            _err(f"Cancel blocked on flagged intake {self.name}", "Flagged Intake Cancel")
            frappe.throw(_("Canceling a flagged intake is prohibited."))

    def on_trash(self) -> None:
        """
        Block delete if intake is flagged.
        """
        if self.intake_status == "Flagged":
            _err(f"Delete blocked on flagged intake {self.name}", "Flagged Intake Delete")
            frappe.throw(_("Deleting a flagged intake is not allowed."))
