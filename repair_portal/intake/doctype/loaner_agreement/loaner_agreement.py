# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/doctype/loaner_agreement/loaner_agreement.py
"""Loaner Agreement DocType controller."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document

_PRINT_FORMAT_NAME = "Loaner Agreement"


class LoanerAgreement(Document):
    """Handles validation and PDF attachment for loaner agreements."""

    def before_insert(self) -> None:
        self.status = "Draft"

    def validate(self) -> None:
        self._validate_required_fields()
        self._ensure_terms_acknowledged()

    def on_submit(self) -> None:
        self.status = "Submitted"
        self._validate_required_fields()
        self._ensure_terms_acknowledged()
        self._attach_pdf()

    def on_cancel(self) -> None:
        self.status = "Draft"

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def _validate_required_fields(self) -> None:
        if not self.linked_loaner:
            frappe.throw(_("Loaner Instrument is required."))
        if not self.borrower_signature:
            frappe.throw(_("Borrower signature is required."))
        if not self.staff_signature:
            frappe.throw(_("Staff signature is required."))

    def _ensure_terms_acknowledged(self) -> None:
        if not self.terms_ack:
            frappe.throw(_("Borrower must acknowledge the terms before submission."))

    def _attach_pdf(self) -> None:
        try:
            pdf_content = frappe.get_print(
                self.doctype,
                self.name,
                _PRINT_FORMAT_NAME,
                as_pdf=True,
            )
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                _(f"Failed to render Loaner Agreement PDF for {self.name}"),
            )
            return

        if not pdf_content:
            return

        file_doc = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": f"{self.name}.pdf",
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "content": pdf_content,
                "is_private": 1,
            }
        )
        file_doc.save(ignore_permissions=True)


def has_permission(doc: LoanerAgreement, ptype: str, user: str) -> bool:
    if ptype in {"read", "write", "create", "delete", "submit", "cancel", "amend"}:
        if user == "Administrator":
            return True
        roles = set(frappe.get_roles(user))
        if roles.intersection({"System Manager", "Intake Coordinator"}):
            return True
        if ptype == "read" and frappe.has_permission("Loaner Instrument", "read", user):
            return True
        return False
    return True
