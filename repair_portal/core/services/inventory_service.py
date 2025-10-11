"""Inventory orchestration for repair operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

from ..contracts import inventory as inventory_contracts
from ..events import publish
from ..registry import EventTopic, Role
from ..security import rate_limited, require_roles

try:
    import frappe
except ImportError:  # pragma: no cover - exercised in integration tests
    frappe = None  # type: ignore

LOGGER_NAME = "repair_portal.inventory"


def _log(message: str, **context: object) -> None:
    if frappe is not None:
        frappe.logger(LOGGER_NAME).info(message, **context)


def _safe_insert(doc: Mapping[str, object]) -> None:
    if frappe is None:
        return
    try:
        frappe.get_doc(dict(doc)).insert(ignore_permissions=True)
    except Exception:  # pragma: no cover - defensive logging
        frappe.log_error(title="Repair inventory insert failed", message=str(doc))


def _issue_stock(request: inventory_contracts.IssueRequest) -> inventory_contracts.StockMovement:
    posting_datetime = datetime.now(timezone.utc)
    movement = inventory_contracts.StockMovement(
        repair_order=request.repair_order,
        item_code=request.item_code,
        serial_no=request.serial_no,
        batch_no=request.batch_no,
        warehouse=request.warehouse,
        quantity=request.quantity,
        posting_datetime=posting_datetime,
        movement_type="issue",
    )
    _safe_insert(
        {
            "doctype": "Repair Material Movement",
            "repair_order": request.repair_order,
            "item_code": request.item_code,
            "warehouse": request.warehouse,
            "serial_no": request.serial_no,
            "batch_no": request.batch_no,
            "qty": request.quantity,
            "movement_type": "Issue",
            "posting_datetime": posting_datetime,
        }
    )
    publish(EventTopic.INVENTORY_ISSUED, movement.dict())
    _log("Inventory issued", **movement.dict())
    return movement


def _return_stock(request: inventory_contracts.ReturnRequest) -> inventory_contracts.StockMovement:
    posting_datetime = datetime.now(timezone.utc)
    movement = inventory_contracts.StockMovement(
        repair_order=request.repair_order,
        item_code=request.item_code,
        serial_no=request.serial_no,
        batch_no=None,
        warehouse=request.warehouse,
        quantity=request.quantity,
        posting_datetime=posting_datetime,
        movement_type="return",
    )
    _safe_insert(
        {
            "doctype": "Repair Material Movement",
            "repair_order": request.repair_order,
            "item_code": request.item_code,
            "warehouse": request.warehouse,
            "serial_no": request.serial_no,
            "qty": request.quantity,
            "movement_type": "Return",
            "posting_datetime": posting_datetime,
            "notes": request.reason,
        }
    )
    publish(EventTopic.INVENTORY_RETURNED, movement.dict())
    _log("Inventory returned", **movement.dict())
    return movement


@require_roles(Role.TECHNICIAN, Role.REPAIR_MANAGER)
@rate_limited("inventory-issue", limit=200, window_seconds=60)
def issue_material(payload: Mapping[str, object]) -> inventory_contracts.StockMovement:
    """Issue material against a Repair Order."""

    request = inventory_contracts.IssueRequest(**payload)
    return _issue_stock(request)


@require_roles(Role.TECHNICIAN, Role.REPAIR_MANAGER)
@rate_limited("inventory-return", limit=200, window_seconds=60)
def return_material(payload: Mapping[str, object]) -> inventory_contracts.StockMovement:
    """Return previously issued material."""

    request = inventory_contracts.ReturnRequest(**payload)
    return _return_stock(request)


@require_roles(Role.REPAIR_MANAGER, Role.CUSTOMER_SERVICE)
@rate_limited("inventory-reserve", limit=100, window_seconds=60)
def reserve_material(payload: Mapping[str, object]) -> inventory_contracts.StockMovement:
    """Reserve material prior to issue."""

    request = inventory_contracts.ReservationRequest(**payload)
    posting_datetime = datetime.now(timezone.utc)
    movement = inventory_contracts.StockMovement(
        repair_order=request.repair_order,
        item_code=request.item_code,
        serial_no=None,
        batch_no=None,
        warehouse=request.warehouse,
        quantity=request.quantity,
        posting_datetime=posting_datetime,
        movement_type="reservation",
    )
    _safe_insert(
        {
            "doctype": "Repair Material Reservation",
            "repair_order": request.repair_order,
            "item_code": request.item_code,
            "warehouse": request.warehouse,
            "qty": request.quantity,
            "require_serial": int(request.require_serial),
            "posting_datetime": posting_datetime,
        }
    )
    publish(EventTopic.INVENTORY_RESERVED, movement.dict())
    _log("Inventory reserved", **movement.dict())
    return movement
