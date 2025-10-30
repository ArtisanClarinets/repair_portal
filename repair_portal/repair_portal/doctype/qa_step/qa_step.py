# Path: repair_portal/repair_portal/doctype/qa_step/qa_step.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for QA Step child table - manages QA process steps and validation.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class QAStep(Document):
    """Child table controller for QA Step records."""

    def validate(self):
        """Validate QA step requirements."""
        if not self.step_name:
            frappe.throw(_("Step Name is required"))