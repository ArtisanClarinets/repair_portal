"""Portal API endpoints for repair operations."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Sequence

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, get_url
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf

from repair_portal.repair_portal.utils import token as token_utils


@frappe.whitelist()
def generate_shipping_label(mail_in_request: str) -> Dict[str, Any]:
    """Create or register a shipping label for a mail-in repair request."""
    doc = frappe.get_doc("Mail In Repair Request", mail_in_request)
    doc.check_permission("write")
    provider = (frappe.conf.get("repair_portal_shipping_provider") or "manual").lower()
    tracking_no = doc.tracking_no
    file_url = doc.label_file
    if provider == "manual" or not frappe.conf.get("repair_portal_shipping_api_key"):
        if not file_url:
            frappe.throw(_("Upload a carrier label before marking the request as issued."))
        _update_mail_in_status(doc, tracking_no or "MANUAL", file_url)
        return {"tracking_no": tracking_no or "MANUAL", "label_url": file_url, "provider": "manual"}
    shipment = _create_shipment(doc)
    label_url, tracking_no = _render_label(doc, shipment)
    _update_mail_in_status(doc, tracking_no, label_url)
    return {"tracking_no": tracking_no, "label_url": label_url, "provider": provider, "shipment": shipment.name}


def _create_shipment(mail_in: Document) -> Document:
    company = frappe.defaults.get_defaults().get("company")
    if not company:
        frappe.throw(_("Set a default company before generating shipping labels."))
    value_of_goods = flt(mail_in.insurance_value or 1)
    shipment = frappe.get_doc(
        {
            "doctype": "Shipment",
            "shipment_type": "Return",
            "pickup_from_type": "Customer",
            "pickup_customer": mail_in.customer,
            "delivery_to_type": "Company",
            "delivery_company": company,
            "pickup_date": nowdate(),
            "pickup_from": "09:00:00",
            "pickup_to": "17:00:00",
            "pickup_address_name": mail_in.customer_address,
            "delivery_address_name": _get_company_address(company),
            "value_of_goods": value_of_goods,
            "description_of_content": _("Clarinet repair shipment"),
        }
    )
    shipment.flags.ignore_permissions = True
    shipment.insert(ignore_mandatory=True)
    return shipment


def _get_company_address(company: str) -> str:
    address = frappe.db.get_value("Company", company, "primary_address")
    if address:
        return address
    address = frappe.db.get_value("Address", {"is_your_company_address": 1}, "name")
    if address:
        return address
    frappe.throw(_("Configure a company address to generate shipping documents."))


def _render_label(mail_in: Document, shipment: Document) -> tuple[str, str]:
    tracking_no = mail_in.tracking_no or frappe.generate_hash(length=12).upper()
    html = frappe.render_template(
        "<html><body><h2>Mail-In Repair Label</h2><p>Shipment: {{ shipment.name }}</p><p>Tracking: {{ tracking }}</p></body></html>",
        {"shipment": shipment, "tracking": tracking_no},
    )
    pdf_bytes = get_pdf(html)
    file_doc = save_file(
        f"Mail-In-Label-{tracking_no}.pdf",
        pdf_bytes,
        dt=mail_in.doctype,
        dn=mail_in.name,
        is_private=1,
    )
    return file_doc.file_url, tracking_no


def _update_mail_in_status(mail_in: Document, tracking_no: str, label_url: str) -> None:
    mail_in.db_set("tracking_no", tracking_no)
    mail_in.db_set("label_file", label_url)
    mail_in.db_set("status", "Label Issued")
    mail_in.reload()
    mail_in.append(
        "shipments",
        {
            "direction": "Inbound",
            "carrier": mail_in.carrier,
            "tracking_no": tracking_no,
            "status": "Label Issued",
            "insurance": mail_in.insurance_value,
        },
    )
    mail_in.save(ignore_permissions=True)


# Rate limit to prevent abuse from anonymous users, which could lead to
# resource exhaustion by creating numerous Repair Estimate and Payment Request docs.
@frappe.whitelist(allow_guest=True, rate_limiter=frappe.rate_limiter(limit=10, seconds=60))
def prepare_quote_and_deposit(
    repair_order: str,
    repair_class: str | None = None,
    upsells: str | Sequence[str] | None = None,
    approval_token: str | None = None,
) -> Dict[str, Any]:
    """Prepare a repair estimate and Stripe deposit payment."""
    order = frappe.get_doc("Repair Order", repair_order)
    estimate = _get_or_create_estimate(order, repair_class)
    if frappe.session.user == "Guest":
        if not approval_token or not token_utils.verify_token(
            estimate.approval_token, approval_token, f"repair-estimate:{estimate.name}"
        ):
            frappe.throw(_("Invalid or expired approval token."), frappe.PermissionError)
    else:
        order.check_permission("write")
    selected = _normalize_upsells(upsells)
    deposit_amount, upsell_rows = _apply_upsells(order, estimate, selected)
    if deposit_amount <= 0:
        frappe.throw(_("Deposit amount must be greater than zero."))
    estimate.deposit_amount = deposit_amount
    estimate.workflow_state = "Awaiting Approval"
    estimate.upsell_selected = []
    for row in upsell_rows:
        estimate.append("upsell_selected", row)
    estimate.save(ignore_permissions=True)
    order.db_set("workflow_state", "Quoted")
    regenerate = frappe.session.user != "Guest"
    token = _ensure_approval_token(estimate) if regenerate else approval_token
    approval_url = get_url(f"/quote/{estimate.name}?token={token}")
    estimate.db_set("approval_link", approval_url)
    payment_request, payment_url = _ensure_payment_request(estimate, deposit_amount)
    frappe.db.commit()
    return {
        "estimate": estimate.name,
        "approval_token": token,
        "payment_request": payment_request.name,
        "payment_url": payment_url,
        "deposit_amount": deposit_amount,
    }


def _get_or_create_estimate(order: Document, repair_class: str | None) -> Document:
    existing = frappe.db.get_value("Repair Estimate", {"repair_order": order.name}, "name")
    if existing:
        return frappe.get_doc("Repair Estimate", existing)
    estimate = frappe.get_doc(
        {
            "doctype": "Repair Estimate",
            "customer": order.customer,
            "instrument": order.instrument,
            "repair_order": order.name,
            "repair_class": repair_class,
        }
    )
    estimate.flags.ignore_permissions = True
    estimate.insert()
    return estimate


def _normalize_upsells(upsells: str | Sequence[str] | None) -> List[str]:
    if not upsells:
        return []
    if isinstance(upsells, str):
        try:
            parsed = json.loads(upsells)
        except json.JSONDecodeError:
            parsed = [upsells]
        else:
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
            return [str(parsed)]
    return [str(item) for item in upsells]


def _apply_upsells(order: Document, estimate: Document, selected: Sequence[str]) -> tuple[float, List[Dict[str, Any]]]:
    template = frappe.get_doc("Repair Class Template", estimate.repair_class) if estimate.repair_class else None
    deposit_ratio = flt(frappe.conf.get("repair_portal_deposit_ratio") or 0.35)
    hourly_rate = flt(frappe.conf.get("repair_portal_hourly_rate") or 125)
    minimum_deposit = flt(frappe.conf.get("repair_portal_minimum_deposit") or 50)
    base_hours = flt(order.planned_hours or 0)
    if not base_hours and template:
        base_hours = flt(template.default_labor_hours or 0)
    base_deposit = max(base_hours * hourly_rate * deposit_ratio, minimum_deposit)
    upsell_total = 0.0
    rows: List[Dict[str, Any]] = []
    if template:
        for option in template.get("upsell_options"):
            accepted = option.item in selected
            if accepted:
                upsell_total += flt(option.price)
            rows.append(
                {
                    "item": option.item,
                    "price": option.price,
                    "description": option.description,
                    "accepted": 1 if accepted else 0,
                }
            )
    return round(base_deposit + upsell_total, 2), rows


def _ensure_approval_token(estimate: Document) -> str:
    raw, hashed = token_utils.generate_token(f"repair-estimate:{estimate.name}")
    estimate.db_set("approval_token", hashed)
    return raw


def _ensure_payment_request(estimate: Document, deposit_amount: float) -> tuple[Document, str]:
    existing = frappe.db.get_value(
        "Payment Request",
        {
            "reference_doctype": "Repair Estimate",
            "reference_name": estimate.name,
            "status": ("in", ["Draft", "Initiated"]),
        },
        "name",
    )
    if existing:
        payment_request = frappe.get_doc("Payment Request", existing)
        if abs(flt(payment_request.grand_total) - deposit_amount) > 0.01:
            payment_request.grand_total = deposit_amount
            payment_request.save(ignore_permissions=True)
        payment_url = payment_request.get_payment_url()
        return payment_request, payment_url
    gateway_account = frappe.db.get_value(
        "Payment Gateway Account", {"payment_gateway": "Stripe", "enabled": 1}, "name"
    )
    if not gateway_account:
        frappe.throw(_("Configure an active Stripe payment gateway account."))
    currency = frappe.defaults.get_global_default("currency") or "USD"
    payment_request = frappe.get_doc(
        {
            "doctype": "Payment Request",
            "payment_request_type": "Inward",
            "payment_gateway_account": gateway_account,
            "payment_gateway": "Stripe",
            "party_type": "Customer",
            "party": estimate.customer,
            "reference_doctype": "Repair Estimate",
            "reference_name": estimate.name,
            "grand_total": deposit_amount,
            "currency": currency,
            "status": "Draft",
            "message": _("Deposit for clarinet repair services."),
        }
    )
    payment_request.flags.ignore_permissions = True
    payment_request.insert()
    payment_request.submit()
    return payment_request, payment_request.get_payment_url()
