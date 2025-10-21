"""SLA related data contracts."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PauseReason(str, Enum):
    """Enumerated pause reasons for SLA tracking."""

    CUSTOMER = "customer"
    PARTS = "parts"
    INTERNAL = "internal"


class SLAEvent(BaseModel):
    repair_order: str = Field(..., description="Repair Order identifier")
    started_at: datetime = Field(..., description="UTC timestamp for event start")
    due_at: datetime = Field(..., description="Computed SLA due timestamp")
    pause_reason: Optional[PauseReason] = Field(
        default=None, description="Reason for pause if state is paused"
    )


class SLATick(BaseModel):
    repair_order: str
    remaining_minutes: int
    status: str = Field(..., description="on_track/at_risk/breached")
    last_transition: Optional[datetime] = None
