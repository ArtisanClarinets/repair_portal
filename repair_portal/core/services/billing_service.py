"""Billing orchestration for repair operations."""

from __future__ import annotations

from typing import Mapping

from ..contracts import billing as billing_contracts
from ..events import publish
from ..registry import EventTopic, Role
from ..security import rate_limited, require_roles

try:
    import frappe
except ImportError:  # pragma: no cover - integration tests handle skip
    frappe = None  # type: ignore

LOGGER_NAME = "repair_portal.billing"


def _log(message: str, **context: object) -> None:
    if frappe is not None:
        frappe.logger(LOGGER_NAME).info(message, **context)


@require_roles(Role.ACCOUNTS, Role.REPAIR_MANAGER)
@rate_limited("billing-build", limit=60, window_seconds=60)
def build_packet(payload: Mapping[str, object]) -> billing_contracts.BillingPacket:
    """Construct a billing packet from labor and material details."""

    packet = billing_contracts.BillingPacket(**payload)
    labor_total = sum(line.amount for line in packet.labor)
    parts_total = sum(line.amount for line in packet.parts)
    packet.total = round(labor_total + parts_total, 2)
    _log("Billing packet built", repair_order=packet.repair_order, total=packet.total)
    publish(EventTopic.BILLING_READY, packet.dict())
    return packet


@require_roles(Role.ACCOUNTS, Role.REPAIR_MANAGER)
@rate_limited("billing-post", limit=60, window_seconds=60)
def mark_invoiced(repair_order: str, invoice: str) -> None:
    """Mark a repair order as invoiced and emit an event."""

    _log("Repair order invoiced", repair_order=repair_order, invoice=invoice)
    if frappe is not None:
        frappe.db.set_value(
            "Repair Order",
            repair_order,
            {"billing_status": "Invoiced", "sales_invoice": invoice},
        )
    publish(EventTopic.INVOICE_POSTED, {"repair_order": repair_order, "invoice": invoice})
