"""Public-facing Mail-In Repair request portal."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, now_datetime

from repair_portal.repair_portal.utils import token as token_utils


@dataclass
class MailInForm:
    full_name: str
    email: str
    phone: str
    marketing_consent: bool
    serial_no: str
    make: str
    model: str
    family: str
    finish: str
    requested_services: str
    preferred_carrier: str
    insurance_value: float
    address_line1: str
    address_line2: str
    city: str
    state: str
    postal_code: str
    country: str
    consent_storage: bool

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "MailInForm":
        missing = [key for key in (
            "full_name",
            "email",
            "serial_no",
            "make",
            "model",
            "family",
            "finish",
            "requested_services",
            "preferred_carrier",
            "address_line1",
            "city",
            "postal_code",
            "country",
        ) if not payload.get(key)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))
        return cls(
            full_name=payload.get("full_name").strip(),
            email=payload.get("email").strip().lower(),
            phone=payload.get("phone", "").strip(),
            marketing_consent=bool(cint(payload.get("marketing_consent"))),
            serial_no=payload.get("serial_no").strip(),
            make=payload.get("make").strip(),
            model=payload.get("model").strip(),
            family=payload.get("family"),
            finish=payload.get("finish"),
            requested_services=payload.get("requested_services").strip(),
            preferred_carrier=payload.get("preferred_carrier"),
            insurance_value=flt(payload.get("insurance_value") or 0),
            address_line1=payload.get("address_line1").strip(),
            address_line2=payload.get("address_line2", "").strip(),
            city=payload.get("city").strip(),
            state=payload.get("state", "").strip(),
            postal_code=payload.get("postal_code").strip(),
            country=payload.get("country").strip(),
            consent_storage=bool(cint(payload.get("consent_storage", 0))),
        )


def get_context(context: Dict[str, Any]) -> Dict[str, Any]:
    context.update(
        {
            "no_cache": 1,
            "show_sidebar": False,
            "title": _("Mail-In Clarinet Repair"),
        }
    )
    return context


@frappe.whitelist(allow_guest=True)
def submit_mail_in_request(data: str) -> Dict[str, Any]:
    payload = json.loads(data)
    form = MailInForm.from_dict(payload)
    if not form.consent_storage:
        frappe.throw(_("Consent is required to process your mail-in repair."))
    customer_name = _ensure_customer(form)
    instrument_name = _ensure_instrument(customer_name, form)
    address_name = _ensure_address(customer_name, form)
    repair_request, portal_token = _create_repair_request(customer_name, instrument_name, form)
    mail_in = _create_mail_in_request(customer_name, instrument_name, address_name, repair_request, form)
    payment_link = _maybe_create_hold(mail_in, customer_name)
    frappe.db.commit()
    return {
        "mail_in_request": mail_in.name,
        "repair_request": repair_request.name,
        "status_page": f"/repair-status/{portal_token}",
        "payment_link": payment_link,
        "portal_token": portal_token,
    }


def _ensure_customer(form: MailInForm) -> str:
    existing = frappe.db.get_value("Customer", {"email_id": form.email})
    if existing:
        return existing
    defaults = frappe.defaults.get_defaults()
    customer_group = defaults.get("customer_group") or frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
    territory = defaults.get("territory") or frappe.db.get_value("Territory", {"is_group": 0}, "name")
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": form.full_name,
            "customer_type": "Individual",
            "customer_group": customer_group,
            "territory": territory,
            "email_id": form.email,
            "mobile_no": form.phone,
        }
    )
    customer.flags.ignore_permissions = True
    customer.insert()
    return customer.name


def _ensure_instrument(customer: str, form: MailInForm) -> str:
    existing = frappe.db.get_value("Instrument", {"serial_no": form.serial_no})
    if existing:
        doc = frappe.get_doc("Instrument", existing)
        if doc.customer != customer:
            doc.customer = customer
            doc.save(ignore_permissions=True)
        return existing
    instrument = frappe.get_doc(
        {
            "doctype": "Instrument",
            "customer": customer,
            "serial_no": form.serial_no,
            "make": form.make,
            "model": form.model,
            "family": form.family,
            "finish": form.finish,
            "portal_visible": 1,
        }
    )
    instrument.flags.ignore_permissions = True
    instrument.insert()
    return instrument.name


def _ensure_address(customer: str, form: MailInForm) -> str:
    existing = frappe.db.get_value(
        "Address",
        {
            "address_line1": form.address_line1,
            "pincode": form.postal_code,
            "city": form.city,
            "email_id": form.email,
        },
        "name",
    )
    if existing:
        return existing
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": form.full_name,
            "address_type": "Shipping",
            "address_line1": form.address_line1,
            "address_line2": form.address_line2,
            "city": form.city,
            "state": form.state,
            "pincode": form.postal_code,
            "country": form.country,
            "email_id": form.email,
            "phone": form.phone,
            "links": [{"link_doctype": "Customer", "link_name": customer}],
        }
    )
    address.flags.ignore_permissions = True
    address.insert()
    return address.name


def _create_repair_request(customer: str, instrument: str, form: MailInForm) -> tuple[Document, str]:
    raw_token, hashed = token_utils.generate_token("repair-request")
    request = frappe.get_doc(
        {
            "doctype": "Repair Request",
            "customer": customer,
            "instrument": instrument,
            "requested_services": form.requested_services,
            "preferred_carrier": form.preferred_carrier,
            "insurance_value": form.insurance_value,
            "portal_token": hashed,
        }
    )
    request.flags.ignore_permissions = True
    request.insert()
    if form.marketing_consent:
        _upsert_player_profile(customer, instrument, form)
    return request, raw_token


def _create_mail_in_request(
    customer: str,
    instrument: str,
    address_name: str,
    repair_request: Document,
    form: MailInForm,
) -> Document:
    mail_in = frappe.get_doc(
        {
            "doctype": "Mail In Repair Request",
            "customer": customer,
            "repair_request": repair_request.name,
            "instrument": instrument,
            "requested_services": form.requested_services,
            "carrier": form.preferred_carrier,
            "insurance_value": form.insurance_value,
            "status": "Draft",
            "arrival_condition_notes": "",
        }
    )
    mail_in.flags.ignore_permissions = True
    mail_in.insert()
    mail_in.db_set("customer_address", address_name)
    return mail_in


def _maybe_create_hold(mail_in: Document, customer: str) -> str | None:
    hold_amount = flt(frappe.conf.get("repair_portal_mail_in_hold_amount") or 1)
    gateway_account = frappe.db.get_value(
        "Payment Gateway Account", {"payment_gateway": "Stripe", "enabled": 1}, "name"
    )
    if hold_amount <= 0 or not gateway_account:
        return None
    currency = frappe.defaults.get_global_default("currency") or "USD"
    payment_request = frappe.get_doc(
        {
            "doctype": "Payment Request",
            "payment_request_type": "Inward",
            "party_type": "Customer",
            "party": customer,
            "reference_doctype": "Mail In Repair Request",
            "reference_name": mail_in.name,
            "payment_gateway_account": gateway_account,
            "payment_gateway": "Stripe",
            "grand_total": hold_amount,
            "currency": currency,
            "status": "Draft",
            "message": _("Authorization hold for mail-in repair intake."),
        }
    )
    payment_request.flags.ignore_permissions = True
    payment_request.insert()
    payment_request.submit()
    return payment_request.get_payment_url()


def _upsert_player_profile(customer: str, instrument: str, form: MailInForm) -> None:
    existing = frappe.db.get_value("Player Profile", {"customer": customer})
    if existing:
        profile = frappe.get_doc("Player Profile", existing)
        profile.marketing_consent = 1
        profile.consent_timestamp = now_datetime()
        if not profile.primary_instrument:
            profile.primary_instrument = instrument
        profile.save(ignore_permissions=True)
        return
    profile = frappe.get_doc(
        {
            "doctype": "Player Profile",
            "customer": customer,
            "primary_instrument": instrument,
            "marketing_consent": 1 if form.marketing_consent else 0,
            "consent_timestamp": now_datetime(),
            "preferences": form.requested_services,
        }
    )
    profile.flags.ignore_permissions = True
    profile.insert()
