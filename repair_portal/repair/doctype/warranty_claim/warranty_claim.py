"""Warranty Claim controller."""
from __future__ import annotations

from typing import Optional

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class WarrantyClaim(Document):
    """Enforce claim lifecycle and linkage to repairs."""

    def before_validate(self) -> None:
        if self.claim_status and self.workflow_state != self.claim_status:
            self.workflow_state = self.claim_status

    def validate(self) -> None:
        self._validate_enrollment_alignment()

    def on_update(self) -> None:
        previous = getattr(self, "_doc_before_save", None)
        if previous is None and hasattr(self, "get_doc_before_save"):
            previous = self.get_doc_before_save()
        previous_status: Optional[str] = getattr(previous, "claim_status", None)
        if self.claim_status != previous_status:
            if self.claim_status in {"Approved", "Denied", "Fulfilled"} and not self.decision_date:
                self.db_set("decision_date", nowdate())
        self._sync_repair_flag()

    def _validate_enrollment_alignment(self) -> None:
        if not self.service_plan_enrollment:
            return
        enrollment = frappe.db.get_value(
            "Service Plan Enrollment",
            self.service_plan_enrollment,
            ["customer", "instrument"],
            as_dict=True,
        )
        if not enrollment:
            frappe.throw("Linked service plan enrollment not found.")
        if enrollment.customer != self.customer:
            frappe.throw("Service plan enrollment belongs to a different customer.")
        if enrollment.instrument != self.instrument:
            frappe.throw("Service plan enrollment is tied to a different instrument.")

    def _sync_repair_flag(self) -> None:
        if not self.repair_order:
            return
        if not frappe.db.exists("Repair Order", self.repair_order):
            return
        if self.claim_status in {"Approved", "Fulfilled"}:
            frappe.db.set_value("Repair Order", self.repair_order, "warranty_flag", 1)
            frappe.db.set_value("Repair Order", self.repair_order, "service_plan_claim", self.service_plan_enrollment)
        elif self.claim_status == "Denied":
            frappe.db.set_value("Repair Order", self.repair_order, "warranty_flag", 0)

