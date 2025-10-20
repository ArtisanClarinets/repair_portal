"""Scheduled tasks that orchestrate cross-module services."""

from __future__ import annotations

from datetime import datetime, timezone

from repair_portal.core.registry import QueueName
from repair_portal.core.services import billing_service, notify_service, sla_service

try:
    import frappe
except ImportError:  # pragma: no cover
    frappe = None  # type: ignore


def _iter_open_orders() -> list[str]:
    if frappe is None or not frappe.db.table_exists("Repair Order"):
        return []
    return [
        row.name
        for row in frappe.get_all("Repair Order", filters={"status": ["not in", ["Completed", "Delivered"]]})
    ]


def sla_breach_scan() -> None:
    """Compute SLA ticks for all open orders and escalate breaches."""

    if frappe is None:
        return
    now = datetime.now(timezone.utc)
    for order in _iter_open_orders():
        tick = sla_service.compute_tick(order)
        status = tick.status.lower()
        if status == "breached":
            frappe.enqueue(
                notify_service.send_customer_message,
                queue=QueueName.REPAIR_NOTIFY.value,
                payload={
                    "repair_order": order,
                    "recipient": frappe.db.get_value("Repair Order", order, "customer_email"),
                    "subject": "Repair SLA Breached",
                    "body": f"Your repair order {order} exceeded the SLA.",
                    "sent_at": now,
                    "via": "email",
                },
            )
        frappe.db.set_value("Repair Order", order, {"sla_status": tick.status, "sla_last_transition": now})


def finalize_billing_packets() -> None:
    """Create billing packets for ready repair orders."""

    if frappe is None:
        return
    orders = frappe.get_all(
        "Repair Order", filters={"billing_status": ["in", ["Ready", "Ready for Billing"]]}, pluck="name"
    )
    for order in orders:
        labor = []
        parts = []
        sessions = []
        packet = billing_service.build_packet(
            {
                "repair_order": order,
                "customer": frappe.db.get_value("Repair Order", order, "customer"),
                "currency": frappe.defaults.get_global_default("currency") or "USD",
                "labor": labor,
                "parts": parts,
                "sessions": sessions,
            }
        )
        frappe.db.set_value("Repair Order", order, "billing_status", "Packet Prepared")
        frappe.logger("repair_portal.billing").info("Billing packet finalised", packet=packet.dict())


def send_feedback_requests() -> None:
    """Send feedback requests for recently delivered orders."""

    if frappe is None:
        return
    delivered_orders = frappe.get_all(
        "Repair Order",
        filters={"status": "Delivered", "feedback_requested_on": ("is", "not set")},
        fields=["name", "customer_email"],
    )
    for order in delivered_orders:
        notify_service.send_customer_message(
            {
                "repair_order": order["name"],
                "recipient": order["customer_email"],
                "subject": "How did we do?",
                "body": "Please let us know about your repair experience.",
                "sent_at": datetime.now(timezone.utc),
                "via": "email",
                "visible_in_portal": True,
            }
        )
        frappe.db.set_value(
            "Repair Order", order["name"], "feedback_requested_on", datetime.now(timezone.utc)
        )
