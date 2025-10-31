# Path: repair_portal/repair_portal/doctype/qa_checklist/qa_checklist.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for QA Checklist - manages quality assurance checklists.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class QAChecklist(Document):
    """Controller for QA Checklist documents."""

    def validate(self):
        """Validate QA checklist requirements."""
        if not self.checklist_name:
            frappe.throw(_("Checklist Name is required"))
        if not self.items:
            frappe.throw(_("At least one checklist item is required"))