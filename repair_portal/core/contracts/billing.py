"""Billing data contracts."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class WorkSession(BaseModel):
    technician: str
    started_at: datetime
    ended_at: datetime
    hours: float = Field(..., gt=0)
    multiplier: float = Field(default=1.0, gt=0)


class LaborLine(BaseModel):
    description: str
    item_code: str
    hours: float
    rate: float
    amount: float


class PartLine(BaseModel):
    item_code: str
    description: str
    quantity: float
    rate: float
    amount: float
    serial_no: Optional[str] = None


class BillingPacket(BaseModel):
    repair_order: str
    customer: str
    currency: str
    labor: List[LaborLine] = Field(default_factory=list)
    parts: List[PartLine] = Field(default_factory=list)
    sessions: List[WorkSession] = Field(default_factory=list)
    total: float = 0.0
