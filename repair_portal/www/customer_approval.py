"""Portal controller for customer approvals."""

from __future__ import annotations

from typing import List

import frappe
from frappe import _
from frappe.utils import get_link_to_form, now_datetime

from repair_portal.repair_portal.doctype.customer_approval.customer_approval import (
    create_customer_approval,
)
from repair_portal.customer.security import ensure_customer_access

login_required = True


def get_context(context):  # noqa: D401
    frappe.only_for(("Customer", "Repair Manager", "System Manager"))
    reference_doctype = frappe.form_dict.get("reference_doctype", "Quotation")
    reference_name = frappe.form_dict.get("reference_name")
    if not reference_name:
        frappe.throw(_("Reference document not specified."))

    doc = frappe.get_doc(reference_doctype, reference_name)
    document_customer = getattr(doc, "customer", None) or getattr(doc, "party_name", None)
    ensure_customer_access(document_customer, frappe.session.user)

    context.reference_doc = doc
    context.reference_link = get_link_to_form(reference_doctype, reference_name)
    context.payment_requests = _payment_requests_for_reference(reference_doctype, reference_name)
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.page_title = _("Customer Approval")
    context.aria_title = _("Repair approval decision")
    context.success_message = None
    context.error_message = None
    context.current_approval = _get_existing_approval(reference_doctype, reference_name)

    if frappe.request.method == "POST":
        try:
            approval = _handle_submission(reference_doctype, reference_name)
            context.current_approval = approval
            context.success_message = _("Your response has been saved.")
        except frappe.ValidationError as exc:
            context.error_message = str(exc)
        except frappe.DuplicateEntryError:
            context.current_approval = _get_existing_approval(reference_doctype, reference_name)
            context.success_message = _("An approval already exists for this document.")

    return context


def _payment_requests_for_reference(reference_doctype: str, reference_name: str) -> List[dict]:
    requests = frappe.get_all(
        "Payment Request",
        filters={"reference_doctype": reference_doctype, "reference_name": reference_name},
        fields=["name", "status", "grand_total", "currency", "mode_of_payment"],
        order_by="creation asc",
    )
    result: List[dict] = []
    for row in requests:
        payment_request = frappe.get_doc("Payment Request", row.name)
        result.append(
            {
                "name": row.name,
                "status": row.status,
                "amount": payment_request.grand_total,
                "currency": payment_request.currency,
                "payment_url": payment_request.get_payment_url(),
                "mode_of_payment": payment_request.mode_of_payment,
            }
        )
    return result


def _handle_submission(reference_doctype: str, reference_name: str):
    action = frappe.form_dict.get("action")
    note = frappe.form_dict.get("note") or None
    terms_version = frappe.form_dict.get("terms_version") or now_datetime().isoformat()
    signer_full_name = frappe.form_dict.get("signer_full_name")
    signer_email = frappe.form_dict.get("signer_email") or frappe.db.get_value(
        "User", frappe.session.user, "email"
    )
    signer_phone = frappe.form_dict.get("signer_phone") or None
    payment_request = frappe.form_dict.get("payment_request") or None
    terms_consent = frappe.form_dict.get("terms_consent") == "on"

    if not signer_full_name:
        frappe.throw(_("Signer name is required."))
    if not terms_consent:
        frappe.throw(_("You must accept the terms to proceed."))

    approval = create_customer_approval(
        reference_doctype=reference_doctype,
        reference_name=reference_name,
        action=action,
        signer_full_name=signer_full_name,
        signer_email=signer_email,
        signer_phone=signer_phone,
        note=note,
        terms_version=terms_version,
        terms_consent=terms_consent,
        payment_request=payment_request,
    )
    return approval


def _get_existing_approval(reference_doctype: str, reference_name: str):
    existing = frappe.get_all(
        "Customer Approval",
        filters={
            "portal_user": frappe.session.user,
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
        },
        order_by="creation desc",
        limit=1,
        pluck="name",
    )
    if not existing:
        return None
    return frappe.get_doc("Customer Approval", existing[0])
