# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/instrument_setup_template/instrument_setup_template.py
# Last Updated: 2025-08-01
# Version: v1.0
# Purpose: Backend controller for Instrument Setup Template Doctype. Manages cloning of templates and auto-updating timestamps for operations.
# Dependencies: Instrument Setup Key Operation, Instrument Category, Instrument Model

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class InstrumentSetupTemplate(Document):
    """Controller for Instrument Setup Template Doctype.
    Handles validation and per-key operation timestamp updates.
    """

    def validate(self):
        """Ensure unique key names within a template and clean data."""
        seen = set()
        for row in self.setup_operations:
            if row.key_name in seen:
                frappe.throw(f"Duplicate key name '{row.key_name}' found in template.")
            seen.add(row.key_name)

    def before_save(self):
        """Auto-fill timestamps when status changes to Completed."""
        for row in self.setup_operations:
            if row.status == "Completed" and not row.timestamp:
                row.timestamp = now_datetime()

    def apply_to_instrument(self, instrument_name: str):
        """Clone this template into a new document instance for a specific instrument job.

        Args:
            instrument_name (str): Target instrument to apply setup template to.
        """
        try:
            new_doc = frappe.new_doc("Instrument Setup Template")
            new_doc.template_name = f"{self.template_name} - {instrument_name}"
            new_doc.instrument_category = self.instrument_category
            new_doc.instrument_model = self.instrument_model
            new_doc.active = 1
            for row in self.setup_operations:
                new_doc.append("setup_operations", {
                    "key_name": row.key_name,
                    "key_code": row.key_code,
                    "operation_type": row.operation_type,
                    "tool_material": row.tool_material,
                    "status": "Draft"
                })
            new_doc.insert(ignore_permissions=True)
            frappe.msgprint(f"Template successfully applied to instrument {instrument_name}.")
            return new_doc.name
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Instrument Setup Template Apply Error")
            frappe.throw("Failed to apply setup template to instrument.")