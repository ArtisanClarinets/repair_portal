"""Customer Approval DocType controller."""

from __future__ import annotations

import hashlib
from typing import Iterable, List

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, format_datetime, get_url_to_form, now_datetime

APPROVAL_PRINT_FORMAT = "Signed Approval Certificate"


class CustomerApproval(Document):
    """Immutable record of a customer approval or decline event."""

    def before_insert(self) -> None:  # noqa: D401
        self._enforce_portal_user()
        self.approval_timestamp = now_datetime()
        self.signer_ip_address = frappe.local.request_ip or "0.0.0.0"
        self.signature_hash = self._build_signature_hash()
        if not self.terms_version:
            self.terms_version = format_datetime(self.approval_timestamp)

    def validate(self) -> None:  # noqa: D401
        if not self.is_new():
            frappe.throw(_("Customer Approvals are immutable once recorded."))
        if not self.terms_consent:
            frappe.throw(_("Terms must be accepted before continuing."))
        self._validate_reference()
        self._prevent_duplicate_action()

    def after_insert(self) -> None:  # noqa: D401
        self._attach_certificate()
        self._notify_parties()

    # --- Helpers -----------------------------------------------------------------
    def _enforce_portal_user(self) -> None:
        session_user = frappe.session.user
        if session_user in {"Guest", "Administrator"}:
            frappe.throw(_("Portal authentication required."))
        self.portal_user = session_user

    def _build_signature_hash(self) -> str:
        payload = "|".join(
            [
                cstr(self.customer),
                cstr(self.portal_user),
                cstr(self.reference_doctype),
                cstr(self.reference_name),
                cstr(self.action),
                cstr(self.signer_full_name),
                cstr(self.signer_email),
                cstr(self.signer_phone),
                cstr(self.note),
                frappe.utils.random_string(12),
            ]
        )
        return hashlib.sha512(payload.encode("utf-8")).hexdigest()

    def _validate_reference(self) -> None:
        if not self.reference_doctype or not self.reference_name:
            frappe.throw(_("Reference document is required."))
        if not frappe.db.exists(self.reference_doctype, self.reference_name):
            frappe.throw(_("Reference document not found."))

    def _prevent_duplicate_action(self) -> None:
        existing = frappe.get_all(
            "Customer Approval",
            filters={
                "portal_user": self.portal_user,
                "reference_doctype": self.reference_doctype,
                "reference_name": self.reference_name,
            },
            pluck="name",
        )
        if existing:
            raise frappe.DuplicateEntryError(  # type: ignore[call-arg]
                _("An approval record already exists for this user and document."),
                existing[0],
            )

    def _attach_certificate(self) -> None:
        try:
            pdf = frappe.attach_print(
                doctype=self.doctype,
                name=self.name,
                print_format=APPROVAL_PRINT_FORMAT,
                doc=self,
                lang=frappe.local.lang,
            )
        except Exception:  # pragma: no cover - logging fallback
            frappe.log_error(frappe.get_traceback(), "Customer Approval PDF generation failed")
            return
        self.db_set("approval_pdf", pdf.get("fname"))

    def _notify_parties(self) -> None:
        subject = _("Customer {0} {1} {2}").format(
            self.customer,
            _("approved") if self.action == "Approved" else _("declined"),
            self.reference_name,
        )
        context = {
            "doc": self,
            "reference_url": get_url_to_form(self.reference_doctype, self.reference_name),
        }
        self._send_email(
            recipients=self._collect_recipient_emails(),
            subject=subject,
            template="customer_approval_received",
            context=context,
        )

    def _collect_recipient_emails(self) -> List[str]:
        recipients: List[str] = []
        if self.signer_email:
            recipients.append(self.signer_email)
        portal_email = frappe.db.get_value("User", self.portal_user, "email")
        if portal_email and portal_email not in recipients:
            recipients.append(portal_email)
        managers = frappe.get_all(
            "Has Role",
            filters={"role": "Repair Manager"},
            distinct=True,
            pluck="parent",
        )
        for user in managers:
            email = frappe.db.get_value("User", user, "email")
            if email and email not in recipients:
                recipients.append(email)
        return recipients

    def _send_email(self, recipients: Iterable[str], subject: str, template: str, context: dict) -> None:
        if not recipients:
            return
        frappe.sendmail(
            recipients=list(recipients),
            subject=subject,
            template=template,
            reference_doctype=self.doctype,
            reference_name=self.name,
            args=context,
            now=True,
        )


def create_customer_approval(
    *,
    reference_doctype: str,
    reference_name: str,
    action: str,
    signer_full_name: str,
    signer_email: str,
    signer_phone: str | None,
    note: str | None,
    terms_version: str,
    terms_consent: bool,
    payment_request: str | None = None,
) -> CustomerApproval:
    """Helper to create an approval ensuring idempotency for the current user."""

    doc = frappe.get_doc(reference_doctype, reference_name)
    customer = getattr(doc, "customer", None) or getattr(doc, "party_name", None)
    if not customer:
        frappe.throw(_("Reference document must be linked to a Customer."))
    if action not in {"Approved", "Declined"}:
        frappe.throw(_("Action must be Approved or Declined."))
    approval = frappe.get_doc(
        {
            "doctype": "Customer Approval",
            "customer": customer,
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "action": action,
            "terms_consent": terms_consent,
            "terms_version": terms_version,
            "signer_full_name": signer_full_name,
            "signer_email": signer_email,
            "signer_phone": signer_phone,
            "note": note,
            "payment_request": payment_request,
        }
    )
    approval.insert(ignore_permissions=False)
    return approval
