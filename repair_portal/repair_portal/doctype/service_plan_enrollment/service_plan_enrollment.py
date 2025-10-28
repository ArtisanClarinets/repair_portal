"""Controller for Service Plan Enrollment."""
from __future__ import annotations

from typing import Optional

import frappe
from frappe.model.document import Document

from repair_portal.repair_portal.service_plans import automation


class ServicePlanEnrollment(Document):
    """Manage lifecycle automation for enrollments."""

    def before_validate(self) -> None:
        if not self.company:
            self.company = frappe.defaults.get_global_default("company")
        if not self.workflow_state:
            self.workflow_state = self.status or "Draft"

    def validate(self) -> None:
        if not self.portal_token:
            automation.ensure_portal_token(self)

    def on_update(self) -> None:
        previous = getattr(self, "_doc_before_save", None)
        if previous is None and hasattr(self, "get_doc_before_save"):
            previous = self.get_doc_before_save()
        previous_status: Optional[str] = getattr(previous, "status", None)
        automation.handle_status_change(self, previous_status)

