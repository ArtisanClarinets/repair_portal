"""Automation helpers for service plan enrollments."""
from __future__ import annotations

from typing import Optional

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, flt, getdate, nowdate

from repair_portal.repair_portal.utils import token as token_utils


FREQUENCY_INTERVAL = {
    "Monthly": ("Month", 1),
    "Yearly": ("Year", 1),
}


def handle_status_change(doc: Document, previous_status: Optional[str]) -> None:
    if doc.status == previous_status:
        return
    if doc.status == "Active":
        activate_enrollment(doc)
    elif doc.status == "Suspended":
        suspend_enrollment(doc)
    elif doc.status == "Expired":
        expire_enrollment(doc)


def activate_enrollment(doc: Document) -> None:
    doc.db_set("workflow_state", "Active")
    ensure_portal_token(doc)
    if doc.auto_pay_enabled:
        ensure_subscription(doc)
    if not doc.next_billing_date:
        doc.db_set("next_billing_date", compute_next_billing_date(doc))
    if not doc.end_date:
        coverage_months = frappe.db.get_value("Service Plan", doc.service_plan, "coverage_months") or 0
        if coverage_months:
            doc.db_set("end_date", add_months(doc.start_date, int(coverage_months)))


def suspend_enrollment(doc: Document) -> None:
    doc.db_set("workflow_state", "Suspended")
    pause_subscription(doc)


def expire_enrollment(doc: Document) -> None:
    doc.db_set("workflow_state", "Expired")
    pause_subscription(doc)


def ensure_portal_token(doc: Document) -> None:
    if doc.portal_token:
        return
    token = token_utils.generate_secure_token(prefix="srv")
    frappe.db.set_value(doc.doctype, doc.name, "portal_token", token)


def compute_next_billing_date(doc: Document) -> str:
    freq = FREQUENCY_INTERVAL.get(doc.billing_frequency)
    if not freq:
        return doc.start_date or nowdate()
    interval, count = freq
    base_date = getdate(doc.start_date or nowdate())
    if interval == "Month":
        return add_months(base_date, count)
    if interval == "Year":
        return add_months(base_date, 12 * count)
    return nowdate()


def ensure_subscription(doc: Document) -> Optional[str]:
    if doc.subscription or not frappe.db.table_exists("tabSubscription"):
        return doc.subscription
    plan_name = ensure_subscription_plan(doc)
    subscription = frappe.new_doc("Subscription")
    subscription.party_type = "Customer"
    subscription.party = doc.customer
    if subscription.meta.has_field("company") and doc.company:
        subscription.company = doc.company
    if subscription.meta.has_field("start_date"):
        subscription.start_date = doc.start_date or nowdate()
    if subscription.meta.has_field("generate_invoice_at"):
        subscription.generate_invoice_at = "Beginning of the current subscription period"
    subscription.append("plans", {"plan": plan_name, "qty": 1})
    subscription.insert(ignore_permissions=True)
    frappe.db.set_value(doc.doctype, doc.name, "subscription", subscription.name)
    return subscription.name


def ensure_subscription_plan(doc: Document) -> str:
    if not frappe.db.table_exists("tabSubscription Plan"):
        frappe.throw(_("Subscription Plan DocType missing."))
    plan = frappe.get_doc("Service Plan", doc.service_plan)
    plan_name = f"Service Plan - {plan.name}"
    if frappe.db.exists("Subscription Plan", plan_name):
        return plan_name
    interval, count = FREQUENCY_INTERVAL.get(doc.billing_frequency, ("Month", 1))
    currency = frappe.get_cached_value("Company", doc.company, "default_currency") if doc.company else None
    if not currency:
        currency = frappe.db.get_single_value("Global Defaults", "default_currency")
    rate = determine_plan_rate(plan.billing_item or plan.item)
    subscription_plan = frappe.get_doc(
        {
            "doctype": "Subscription Plan",
            "plan_name": plan_name,
            "currency": currency,
            "item": plan.billing_item or plan.item,
            "price_determination": "Fixed Rate",
            "billing_interval": interval,
            "billing_interval_count": count,
            "cost": rate,
        }
    )
    subscription_plan.insert(ignore_permissions=True)
    return subscription_plan.name


def determine_plan_rate(item_code: Optional[str]) -> float:
    if not item_code:
        return 0.0
    return flt(
        frappe.db.get_value(
            "Item Price",
            {
                "item_code": item_code,
                "selling": 1,
            },
            "price_list_rate",
        )
    )


def pause_subscription(doc: Document) -> None:
    if not doc.subscription or not frappe.db.exists("Subscription", doc.subscription):
        return
    subscription = frappe.get_doc("Subscription", doc.subscription)
    if subscription.meta.has_field("status"):
        subscription.status = "Cancelled"
    subscription.save(ignore_permissions=True)


def queue_renewal_notifications() -> None:
    today = getdate(nowdate())
    remind_before = cint(frappe.db.get_single_value("Repair Portal Settings", "renewal_notice_days") or 7)
    window_start = add_days(today, remind_before)
    enrollments = frappe.get_all(
        "Service Plan Enrollment",
        filters={
            "status": "Active",
            "next_billing_date": ("<=", window_start),
        },
        fields=["name", "customer", "next_billing_date", "portal_token"],
    )
    for row in enrollments:
        send_renewal_notification(row)


def send_renewal_notification(enrollment_row: dict) -> None:
    subject = _("Service Plan Renewal Reminder")
    portal_link = frappe.utils.get_url(f"/service-plans?token={enrollment_row['portal_token']}")
    message = _(
        "Your service plan will renew on {date}. Review details here: {link}"
    ).format(date=enrollment_row["next_billing_date"], link=portal_link)
    frappe.sendmail(
        recipients=[frappe.db.get_value("Customer", enrollment_row["customer"], "email_id")],
        subject=subject,
        message=message,
        now=True,
    )


def process_autopay() -> None:
    today = nowdate()
    enrollments = frappe.get_all(
        "Service Plan Enrollment",
        filters={
            "status": "Active",
            "auto_pay_enabled": 1,
            "next_billing_date": ("<=", today),
        },
        fields=["name"],
    )
    for row in enrollments:
        doc = frappe.get_doc("Service Plan Enrollment", row.name)
        try:
            create_payment_request(doc)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Service Plan autopay failure for {doc.name}")


def create_payment_request(doc: Document) -> None:
    amount = determine_plan_rate(
        frappe.db.get_value("Service Plan", doc.service_plan, "billing_item")
        or frappe.db.get_value("Service Plan", doc.service_plan, "item")
    )
    if not amount:
        return
    if frappe.db.exists(
        "Payment Request",
        {
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "status": ("in", ["Initiated", "Requested"]),
        },
    ):
        return
    gateway = frappe.conf.get("repair_portal_stripe_gateway")
    if not gateway:
        frappe.log_error("Stripe gateway not configured", "Service Plan autopay")
        return
    payment_request = frappe.get_doc(
        {
            "doctype": "Payment Request",
            "payment_gateway_account": gateway,
            "payment_request_type": "Inward",
            "party_type": "Customer",
            "party": doc.customer,
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "grand_total": amount,
            "message": _("Service plan renewal for {plan}").format(plan=doc.service_plan),
        }
    )
    payment_request.flags.ignore_permissions = True
    payment_request.insert()
    payment_request.submit()
    doc.db_set("last_billed_on", nowdate())
    doc.db_set("next_billing_date", compute_next_billing_date(doc))


def cint(value: Optional[str]) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

