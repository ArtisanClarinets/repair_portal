"""Rental Contract DocType controller."""
from __future__ import annotations

from typing import Optional

import frappe
from frappe.model.document import Document

from repair_portal.repair_portal.rental import rental_controller


class RentalContract(Document):
    """Lifecycle hooks for rental contracts."""

    def before_validate(self) -> None:
        if not self.company:
            self.company = frappe.defaults.get_global_default("company")
        if not self.barcode:
            rental_controller.ensure_barcode(self)

    def on_update(self) -> None:
        previous = getattr(self, "_doc_before_save", None)
        if previous is None and hasattr(self, "get_doc_before_save"):
            previous = self.get_doc_before_save()
        previous_status: Optional[str] = getattr(previous, "status", None)
        rental_controller.handle_status_change(self, previous_status)

    def validate(self) -> None:
        if self.status == "Active":
            rental_controller.validate_unique_serial(self)

    def before_save(self) -> None:
        # Align workflow_state with explicit status changes during manual edits
        if self.workflow_state != self.status:
            self.workflow_state = self.status

