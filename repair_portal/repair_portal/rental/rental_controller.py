"""Rental automation for Repair Portal."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, nowdate

from repair_portal.repair_portal.utils import barcode as barcode_utils


@dataclass
class PlanInterval:
    interval: str
    count: int


BILLING_TO_INTERVAL = {
    "Monthly": PlanInterval("Month", 1),
    "Quarterly": PlanInterval("Month", 3),
    "Yearly": PlanInterval("Year", 1),
}


def handle_status_change(doc: Document, previous_status: Optional[str]) -> None:
    """Dispatch lifecycle automation when a rental contract state changes."""
    current = doc.status
    if current == previous_status:
        return

    if current == "Active":
        activate_contract(doc)
    elif current == "Returned":
        mark_returned(doc)
    elif current == "Overdue":
        frappe.db.set_value(doc.doctype, doc.name, "workflow_state", "Overdue")
    elif current == "Draft":
        frappe.db.set_value(doc.doctype, doc.name, "workflow_state", "Draft")


def activate_contract(doc: Document) -> None:
    """Create downstream billing + logistics artifacts when a rental activates."""
    frappe.db.set_value(doc.doctype, doc.name, "workflow_state", "Active")
    validate_unique_serial(doc)
    ensure_subscription(doc)
    ensure_delivery_note(doc)
    reserve_serial_no(doc)
    ensure_barcode(doc)


def mark_returned(doc: Document) -> None:
    """Finalize the rental: restock instrument, close subscription, and bill damages."""
    frappe.db.set_value(doc.doctype, doc.name, "workflow_state", "Returned")
    if not doc.return_date:
        frappe.db.set_value(doc.doctype, doc.name, "return_date", nowdate())

    close_subscription(doc)
    release_serial_no(doc)
    restock_via_delivery_note(doc)
    total_charge = sum(flt(row.charge_amount) for row in doc.get("inspection_findings", []) if cint(row.bill_customer))
    if total_charge > 0:
        invoice = create_damage_invoice(doc, total_charge)
        if invoice:
            frappe.db.set_value(doc.doctype, doc.name, "damage_invoice", invoice)


def validate_unique_serial(doc: Document) -> None:
    if not doc.serial_no:
        frappe.throw("Serial number is required to activate a rental contract.")
    conflict = frappe.db.exists(
        doc.doctype,
        {
            "name": ("!=", doc.name),
            "serial_no": doc.serial_no,
            "status": ("in", ["Active", "Overdue"]),
        },
    )
    if conflict:
        frappe.throw(f"Serial {doc.serial_no} is already assigned to another active rental ({conflict}).")


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
        frappe.throw("Subscription Plan DocType missing. Install ERPNext Subscriptions module.")

    plan_name = f"Rental - {doc.billing_plan}"
    if frappe.db.exists("Subscription Plan", plan_name):
        return plan_name

    defaults = BILLING_TO_INTERVAL.get(doc.billing_plan)
    if not defaults:
        frappe.throw(f"Unsupported billing plan {doc.billing_plan}.")

    currency = frappe.get_cached_value("Company", doc.company, "default_currency") if doc.company else None
    if not currency:
        currency = frappe.db.get_single_value("Global Defaults", "default_currency")

    plan = frappe.get_doc(
        {
            "doctype": "Subscription Plan",
            "plan_name": plan_name,
            "currency": currency,
            "item": doc.billing_item or doc.instrument,
            "price_determination": "Fixed Rate",
            "billing_interval": defaults.interval,
            "billing_interval_count": defaults.count,
        }
    )
    rate = determine_rental_rate(doc)
    if plan.meta.has_field("cost"):
        plan.cost = rate
    plan.insert(ignore_permissions=True)
    return plan.name


def determine_rental_rate(doc: Document) -> float:
    item_code = doc.billing_item or doc.instrument
    if not item_code:
        return 0.0
    price = frappe.db.get_value(
        "Item Price",
        {
            "item_code": item_code,
            "selling": 1,
        },
        "price_list_rate",
    )
    return flt(price)


def ensure_delivery_note(doc: Document) -> Optional[str]:
    if doc.delivery_note:
        return doc.delivery_note
    if not frappe.db.table_exists("tabDelivery Note"):
        return None

    delivery_note = frappe.new_doc("Delivery Note")
    delivery_note.customer = doc.customer
    if delivery_note.meta.has_field("company") and doc.company:
        delivery_note.company = doc.company
    if delivery_note.meta.has_field("posting_date"):
        delivery_note.posting_date = doc.start_date or nowdate()
    item_row = {
        "item_code": doc.instrument,
        "qty": 1,
    }
    if doc.warehouse:
        item_row["warehouse"] = doc.warehouse
    if doc.serial_no:
        item_row["serial_no"] = doc.serial_no
    delivery_note.append("items", item_row)
    delivery_note.insert(ignore_permissions=True)
    delivery_note.submit()
    frappe.db.set_value(doc.doctype, doc.name, "delivery_note", delivery_note.name)
    return delivery_note.name


def restock_via_delivery_note(doc: Document) -> None:
    if not doc.delivery_note or not frappe.db.exists("Delivery Note", doc.delivery_note):
        return
    delivery_note = frappe.get_doc("Delivery Note", doc.delivery_note)
    if delivery_note.docstatus != 1:
        return
    if delivery_note.meta.has_field("is_return"):
        return  # already reversed
    return_dn = frappe.copy_doc(delivery_note)
    return_dn.name = None
    return_dn.is_return = 1
    return_dn.return_against = delivery_note.name
    for item in return_dn.items:
        item.qty = -abs(flt(item.qty))
    return_dn.insert(ignore_permissions=True)
    return_dn.submit()


def reserve_serial_no(doc: Document) -> None:
    if not doc.serial_no or not frappe.db.table_exists("tabSerial No"):
        return
    try:
        from erpnext.stock.doctype.serial_no.serial_no import assign_serial_no_to_customer
    except Exception:
        return
    assign_serial_no_to_customer(doc.serial_no, doc.customer)


def release_serial_no(doc: Document) -> None:
    if not doc.serial_no or not frappe.db.table_exists("tabSerial No"):
        return
    try:
        from erpnext.stock.doctype.serial_no.serial_no import return_serial_no
    except Exception:
        return
    return_serial_no(doc.serial_no)


def close_subscription(doc: Document) -> None:
    if not doc.subscription or not frappe.db.exists("Subscription", doc.subscription):
        return
    subscription = frappe.get_doc("Subscription", doc.subscription)
    if subscription.docstatus == 2:
        return
    if subscription.meta.has_field("status"):
        subscription.status = "Cancelled"
    if subscription.meta.has_field("cancellation_date"):
        subscription.cancellation_date = getdate(nowdate())
    subscription.save(ignore_permissions=True)


def create_damage_invoice(doc: Document, total_charge: float) -> Optional[str]:
    if not frappe.db.table_exists("tabSales Invoice"):
        return None
    if doc.damage_invoice and frappe.db.exists("Sales Invoice", doc.damage_invoice):
        return doc.damage_invoice
    item_code = doc.damage_item or doc.billing_item or doc.instrument
    if not item_code:
        return None
    invoice = frappe.new_doc("Sales Invoice")
    invoice.customer = doc.customer
    if invoice.meta.has_field("company") and doc.company:
        invoice.company = doc.company
    invoice.append(
        "items",
        {
            "item_code": item_code,
            "qty": 1,
            "rate": total_charge,
        },
    )
    invoice.flags.ignore_permissions = True
    invoice.insert()
    invoice.submit()
    return invoice.name


def ensure_barcode(doc: Document) -> None:
    if getattr(doc, "barcode", None):
        return
    new_code = barcode_utils.generate_barcode_value(prefix="RENT", name=doc.name)
    frappe.db.set_value(doc.doctype, doc.name, "barcode", new_code)

