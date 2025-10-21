"""Service helpers for SLA lifecycle management."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from ..contracts import sla as sla_contracts
from ..events import publish
from ..registry import EventTopic, Role
from ..security import rate_limited, require_roles

try:
    import frappe
except ImportError:  # pragma: no cover - exercised in integration tests
    frappe = None  # type: ignore

LOGGER_NAME = "repair_portal.sla"


def _log(message: str, **context: object) -> None:
    if frappe is not None:
        frappe.logger(LOGGER_NAME).info(message, **context)


@require_roles(Role.REPAIR_MANAGER, Role.CUSTOMER_SERVICE)
@rate_limited("sla-start", limit=30, window_seconds=60)
def start_sla(
    repair_order: str, due_at: datetime, started_at: Optional[datetime] = None
) -> sla_contracts.SLAEvent:
    """Start an SLA clock for a repair order."""

    started = started_at or datetime.now(timezone.utc)
    event = sla_contracts.SLAEvent(repair_order=repair_order, started_at=started, due_at=due_at)
    _log("SLA started", repair_order=repair_order, due_at=due_at.isoformat())
    if frappe is not None:
        frappe.db.set_value("Repair Order", repair_order, {"sla_started_on": started, "sla_due_on": due_at})
    publish(EventTopic.SLA_STARTED, event.dict())
    return event


@require_roles(Role.REPAIR_MANAGER, Role.TECHNICIAN)
@rate_limited("sla-pause", limit=60, window_seconds=60)
def pause_sla(repair_order: str, reason: sla_contracts.PauseReason) -> sla_contracts.SLAEvent:
    """Pause an active SLA and emit an event."""

    now = datetime.now(timezone.utc)
    due_at = now
    if frappe is not None:
        due_at = frappe.db.get_value("Repair Order", repair_order, "sla_due_on") or now
        frappe.db.set_value(
            "Repair Order", repair_order, {"sla_paused_on": now, "sla_pause_reason": reason.value}
        )
    event = sla_contracts.SLAEvent(
        repair_order=repair_order, started_at=now, due_at=due_at, pause_reason=reason
    )
    _log("SLA paused", repair_order=repair_order, reason=reason.value)
    publish(EventTopic.SLA_PAUSED, event.dict())
    return event


@require_roles(Role.REPAIR_MANAGER, Role.TECHNICIAN)
@rate_limited("sla-resume", limit=60, window_seconds=60)
def resume_sla(repair_order: str, due_at: datetime) -> sla_contracts.SLAEvent:
    """Resume a paused SLA."""

    now = datetime.now(timezone.utc)
    if frappe is not None:
        frappe.db.set_value("Repair Order", repair_order, {"sla_paused_on": None, "sla_pause_reason": None})
    event = sla_contracts.SLAEvent(repair_order=repair_order, started_at=now, due_at=due_at)
    _log("SLA resumed", repair_order=repair_order, due_at=due_at.isoformat())
    publish(EventTopic.SLA_RESUMED, event.dict())
    return event


def compute_tick(repair_order: str) -> sla_contracts.SLATick:
    """Compute a snapshot of remaining SLA time for dashboards."""

    now = datetime.now(timezone.utc)
    due_at = now
    last_transition = None
    status = "unknown"

    if frappe is not None:
        doc = frappe.db.get_value(
            "Repair Order",
            repair_order,
            ["sla_due_on", "sla_status", "sla_last_transition"],
            as_dict=True,
        )
        if doc:
            due_at = doc.get("sla_due_on") or now
            status = doc.get("sla_status") or "unknown"
            last_transition = doc.get("sla_last_transition")
    remaining = int((due_at - now).total_seconds() // 60)
    tick = sla_contracts.SLATick(
        repair_order=repair_order,
        remaining_minutes=remaining,
        status=status,
        last_transition=last_transition,
    )
    _log("SLA tick", repair_order=repair_order, remaining=remaining, status=status)
    return tick
