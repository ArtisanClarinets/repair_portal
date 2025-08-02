# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/instrument_setup_key_operation/instrument_setup_key_operation.py
# Last Updated: 2025-08-01
# Version: v1.0
# Purpose: Server-side controller for Instrument Setup Key Operation child table Doctype. Handles any validations or automation when a technician records key-specific setup operations.
# Dependencies: frappe, ERPNext framework

import frappe
from frappe.model.document import Document

class InstrumentSetupKeyOperation(Document):
    """Server-side logic for Instrument Setup Key Operation Doctype.

    This class provides hooks for validation, before save, and after save events for each key operation
    performed on an instrument during setup.
    """

    def validate(self):
        """Ensure required data consistency before saving the record."""
        if not self.key_name:
            frappe.throw("Key Name is required for each operation entry.")

        if not self.operation_type:
            frappe.throw("Operation Type cannot be empty.")

    def before_save(self):
        """Set default timestamp if status is Completed and no timestamp provided."""
        if self.status == "Completed" and not self.timestamp:
            self.timestamp = frappe.utils.now_datetime()

    def on_update(self):
        """Log updates for auditing purposes."""
        try:
            frappe.logger().info(f"Instrument Setup Key Operation updated: {self.name} ({self.key_name})")
        except Exception as e:
            frappe.log_error(f"Error logging Instrument Setup Key Operation update: {str(e)}")
