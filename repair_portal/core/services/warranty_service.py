"""Warranty support service."""

from __future__ import annotations

from typing import Mapping

from ..contracts import warranty as warranty_contracts
from ..events import publish
from ..registry import EventTopic, Role
from ..security import rate_limited, require_roles

try:
    import frappe
except ImportError:  # pragma: no cover
    frappe = None  # type: ignore

LOGGER_NAME = "repair_portal.warranty"


def _log(message: str, **context: object) -> None:
    if frappe is not None:
        frappe.logger(LOGGER_NAME).info(message, **context)


@require_roles(Role.REPAIR_MANAGER, Role.CUSTOMER_SERVICE)
@rate_limited("warranty-adjust", limit=60, window_seconds=60)
def post_adjustment(payload: Mapping[str, object]) -> warranty_contracts.WarrantyAdjustment:
    """Persist a warranty adjustment and emit the related event."""

    adjustment = warranty_contracts.WarrantyAdjustment(**payload)
    _log("Warranty adjustment", repair_order=adjustment.repair_order, minutes=adjustment.adjustment_minutes)
    if frappe is not None:
        doc = frappe.get_doc(
            {
                "doctype": "Repair Warranty Adjustment",
                "repair_order": adjustment.repair_order,
                "instrument": adjustment.instrument,
                "adjustment_minutes": adjustment.adjustment_minutes,
                "reason": adjustment.reason,
                "adjusted_by": adjustment.adjusted_by,
                "adjusted_at": adjustment.adjusted_at,
            }
        )
        doc.flags.ignore_permissions = True
        doc.insert()
    publish(EventTopic.WARRANTY_ADJUSTED, adjustment.dict())
    return adjustment


def current_status(instrument: str) -> warranty_contracts.WarrantyStatus | None:
    """Return the current warranty status for an instrument."""

    if frappe is None:
        return None
    record = frappe.db.get_value(
        "Warranty Status",
        {"instrument": instrument},
        ["instrument", "coverage_until", "terms", "is_active"],
        as_dict=True,
    )
    if not record:
        return None
    return warranty_contracts.WarrantyStatus(**record)
