# Path: repair_portal/repair_portal/doctype/repair_class_template/repair_class_template.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Repair Class Template - manages repair class templates.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class RepairClassTemplate(Document):
    """Controller for Repair Class Template documents."""

    def validate(self):
        """Validate repair class template requirements."""
        if not self.template_name:
            frappe.throw(_("Template Name is required"))
        if not self.repair_class:
            frappe.throw(_("Repair Class is required"))