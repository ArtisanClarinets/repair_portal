"""Warranty contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WarrantyStatus(BaseModel):
    instrument: str
    coverage_until: Optional[datetime]
    terms: Optional[str]
    is_active: bool = True


class WarrantyAdjustment(BaseModel):
    repair_order: str
    instrument: str
    adjustment_minutes: int = Field(..., description="Positive or negative minutes")
    reason: str
    adjusted_by: str
    adjusted_at: datetime
