"""Inventory service contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReservationRequest(BaseModel):
    repair_order: str
    item_code: str
    warehouse: str
    quantity: float = Field(..., gt=0)
    require_serial: bool = False


class IssueRequest(BaseModel):
    repair_order: str
    item_code: str
    warehouse: str
    quantity: float = Field(..., gt=0)
    serial_no: Optional[str] = None
    batch_no: Optional[str] = None


class ReturnRequest(BaseModel):
    repair_order: str
    item_code: str
    warehouse: str
    quantity: float = Field(..., gt=0)
    serial_no: Optional[str] = None
    reason: Optional[str] = None


class StockMovement(BaseModel):
    repair_order: str
    item_code: str
    serial_no: Optional[str]
    batch_no: Optional[str]
    warehouse: str
    quantity: float
    posting_datetime: datetime
    movement_type: str = Field(..., description="issue/return/reservation")
