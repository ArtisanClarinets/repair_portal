"""Capacity and SLA utilities for Repair Order."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Iterable

import frappe
from frappe.utils import cint, flt, get_datetime, getdate, now_datetime

OPEN_STATES = {
    "Requested",
    "Awaiting Arrival",
    "Checked-In",
    "Quoted",
    "Approved",
    "In Progress",
    "QC",
    "Ready to Ship",
}


@dataclass
class CapacitySnapshot:
    sla_due: datetime
    utilization: float
    risk: str


def _normalize_start(doc: frappe.Document) -> datetime:
    start = doc.get("scheduled_start")
    if start:
        return get_datetime(start)
    start = now_datetime()
    doc.scheduled_start = start
    return start


def _iter_availability(technician: str, start: datetime) -> Iterable[tuple[datetime, int]]:
    filters = {
        "technician": technician,
        "date": (">=", getdate(start)),
    }
    rows = frappe.get_all(
        "Technician Availability",
        filters=filters,
        fields=["date", "available_minutes"],
        order_by="date asc",
        limit=30,
    )
    for row in rows:
        date_value = getdate(row.date)
        minutes = cint(row.available_minutes or 0)
        yield datetime.combine(date_value, time.min), minutes


def _calculate_capacity(doc: frappe.Document) -> CapacitySnapshot:
    planned_minutes = int(flt(doc.get("planned_hours") or 0) * 60)
    if planned_minutes <= 0 or not doc.get("technician"):
        start = _normalize_start(doc)
        return CapacitySnapshot(sla_due=start, utilization=0.0, risk="Low")

    start = _normalize_start(doc)
    minutes_remaining = planned_minutes
    total_available = 0
    scheduled_end = start

    for day_start, available in _iter_availability(doc.technician, start):
        if available <= 0:
            continue
        total_available += available
        daily_start = scheduled_end if getdate(scheduled_end) == getdate(day_start) else day_start.replace(
            hour=9, minute=0
        )
        consumed = min(minutes_remaining, available)
        scheduled_end = daily_start + timedelta(minutes=consumed)
        minutes_remaining -= consumed
        if minutes_remaining <= 0:
            break

    if minutes_remaining > 0:
        scheduled_end = scheduled_end + timedelta(minutes=minutes_remaining)

    if total_available <= 0:
        utilization = 1.0
        risk = "High"
    else:
        utilization = planned_minutes / float(total_available)
        if utilization <= 0.7:
            risk = "Low"
        elif utilization <= 1.0:
            risk = "Medium"
        else:
            risk = "High"

    return CapacitySnapshot(sla_due=scheduled_end, utilization=utilization * 100.0, risk=risk)


def update_capacity_fields(doc: frappe.Document, _event: str | None = None) -> CapacitySnapshot:
    snapshot = _calculate_capacity(doc)
    doc.sla_due = snapshot.sla_due
    doc.scheduled_end = snapshot.sla_due
    doc.capacity_score = snapshot.utilization
    doc.sla_risk = snapshot.risk
    return snapshot


def on_update_after_submit(doc: frappe.Document, _event: str | None = None) -> None:
    snapshot = update_capacity_fields(doc)
    frappe.db.set_value(
        "Repair Order",
        doc.name,
        {
            "sla_due": snapshot.sla_due,
            "scheduled_end": snapshot.sla_due,
            "capacity_score": snapshot.utilization,
            "sla_risk": snapshot.risk,
        },
        update_modified=False,
    )


def recompute_capacity_snapshot() -> None:
    """Nightly task to keep SLA forecasts current."""
    names = frappe.get_all(
        "Repair Order",
        filters={"workflow_state": ("in", list(OPEN_STATES))},
        pluck="name",
    )
    for name in names:
        doc = frappe.get_doc("Repair Order", name)
        snapshot = update_capacity_fields(doc)
        frappe.db.set_value(
            "Repair Order",
            name,
            {
                "sla_due": snapshot.sla_due,
                "scheduled_end": snapshot.sla_due,
                "capacity_score": snapshot.utilization,
                "sla_risk": snapshot.risk,
            },
            update_modified=False,
        )
