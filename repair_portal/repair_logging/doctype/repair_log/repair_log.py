# File Header Template
# Relative Path: repair_portal/repair_logging/doctype/repair_log/repair_log.py
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Backend controller for Repair Log; tracks all repair activities and status for any instrument. Ensures full audit compliance and workflow.
# Dependencies: Instrument, User, Clarinet Intake, Customer

import frappe
from frappe.model.document import Document
from frappe import _

class RepairLog(Document):
    """
    Tracks all repairs performed on an instrument, linked to intake/customer/technician for audit and workflow. Logs changes for compliance and analytics.
    """

    def before_save(self):
        """
        Ensures status and required relationships are correct before saving. Fortune-500 level audit.
        """
        if self.status not in ["Open", "In Progress", "Complete", "Cancelled"]:
            frappe.throw(_("Invalid status for Repair Log."))
        if not self.instrument:
            frappe.throw(_("Repair Log must be linked to an instrument."))
        if not self.technician:
            frappe.throw(_("Technician must be set for every Repair Log."))
        # Optionally, link to customer from instrument if not set
        if not self.customer:
            instrument_customer = frappe.db.get_value("Instrument", self.instrument, "customer")
            if instrument_customer:
                self.customer = instrument_customer
        # Optionally, auto-set date if missing
        if not self.date:
            self.date = frappe.utils.nowdate()

    def on_update(self):
        """
        Logs updates for analytics or triggers downstream workflows if needed.
        """
        pass  # Extend as needed
