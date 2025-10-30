"""Utility to provision demo approval + payment artifacts."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import today

from repair_portal.repair_portal.doctype.customer_approval.customer_approval import (
    create_customer_approval,
)
from repair_portal.repair_portal.doctype.customer_approval import payment_hooks


def run() -> None:
    """Create a demo quotation, payment request, and approval for training environments."""

    customer, portal_user = _ensure_customer()
    quotation = _ensure_quotation(customer)
    payment_request = _ensure_payment_request(customer, quotation)
    _ensure_customer_approval(quotation, portal_user)
    _simulate_payment(payment_request)
    frappe.db.commit()
    frappe.msgprint(
        _( "Demo artifacts created for customer {0}. Payment Request: {1}").format(
            customer.name, payment_request.name
        )
    )


def _ensure_customer():
    customer_name = "Demo Portal Customer"
    customer = frappe.db.exists("Customer", {"customer_name": customer_name})
    if customer:
        doc = frappe.get_doc("Customer", customer)
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": "Individual",
                "email_id": "demo-portal@example.com",
            }
        ).insert()
    portal_user = _ensure_portal_user(doc)
    return doc, portal_user


def _ensure_portal_user(customer):
    user_email = customer.email_id or "demo-portal@example.com"
    user = frappe.db.exists("User", {"email": user_email})
    if user:
        return frappe.get_doc("User", user)
    doc = frappe.get_doc(
        {
            "doctype": "User",
            "email": user_email,
            "send_welcome_email": 0,
            "first_name": "Demo",
            "roles": [{"role": "Customer"}],
        }
    ).insert()
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": "Demo",
            "user": doc.name,
            "email_id": user_email,
        }
    ).insert()
    contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})
    contact.save()
    return doc


def _ensure_quotation(customer):
    quotation = frappe.db.exists(
        "Quotation",
        {
            "customer": customer.name,
            "transaction_date": today(),
            "docstatus": 0,
        },
    )
    if quotation:
        return frappe.get_doc("Quotation", quotation)
    item_code = frappe.db.get_value("Item", {"item_code": "PORTAL-ITEM"}, "name")
    if not item_code:
        item_doc = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": "PORTAL-ITEM",
                "item_name": "Portal Service",
                "item_group": frappe.db.get_default("item_group") or "Products",
                "stock_uom": "Nos",
                "is_sales_item": 1,
            }
        ).insert()
        item_code = item_doc.name
    doc = frappe.get_doc(
        {
            "doctype": "Quotation",
            "quotation_to": "Customer",
            "party_name": customer.name,
            "customer": customer.name,
            "transaction_date": today(),
            "company": frappe.db.get_default("company") or frappe.db.get_value("Company", {}, "name"),
            "items": [
                {
                    "item_code": item_code,
                    "item_name": "Portal Service",
                    "qty": 1,
                    "rate": 150,
                }
            ],
        }
    )
    return doc.insert()


def _ensure_payment_request(customer, quotation):
    existing = frappe.db.exists(
        "Payment Request",
        {
            "reference_doctype": "Quotation",
            "reference_name": quotation.name,
            "docstatus": 0,
        },
    )
    if existing:
        return frappe.get_doc("Payment Request", existing)
    doc = frappe.get_doc(
        {
            "doctype": "Payment Request",
            "payment_request_type": "Inward",
            "party_type": "Customer",
            "party": customer.name,
            "customer": customer.name,
            "transaction_date": today(),
            "reference_doctype": "Quotation",
            "reference_name": quotation.name,
            "grand_total": 150,
            "currency": frappe.db.get_default("currency") or "USD",
            "mode_of_payment": "Cash",
            "status": "Initiated",
            "contact_email": customer.email_id,
        }
    )
    return doc.insert()


def _ensure_customer_approval(quotation, portal_user):
    existing = frappe.db.exists(
        "Customer Approval",
        {"reference_doctype": "Quotation", "reference_name": quotation.name},
    )
    if existing:
        return frappe.get_doc("Customer Approval", existing)
    original_user = frappe.session.user
    try:
        frappe.set_user(portal_user.name)
        return create_customer_approval(
            reference_doctype="Quotation",
            reference_name=quotation.name,
            action="Approved",
            signer_full_name="Demo Signer",
            signer_email=portal_user.email,
            signer_phone="000-0000",
            note="Demo approval generated via runbook.",
            terms_version="demo",
            terms_consent=True,
        )
    finally:
        frappe.set_user(original_user)


def _simulate_payment(payment_request):
    if payment_request.status in {"Completed", "Paid"}:
        return
    payment_request.status = "Completed"
    payment_request.flags.repair_portal_payment_notified = False
    payment_hooks.handle_payment_request_update(payment_request, "on_update")
