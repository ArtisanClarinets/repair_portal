"""Messaging contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CustomerMessage(BaseModel):
    repair_order: str
    recipient: str
    subject: str
    body: str
    sent_at: datetime
    via: str = Field(..., description="email/sms/portal")
    visible_in_portal: bool = False


class PortalVisibility(BaseModel):
    repair_order: str
    visible: bool
    reason: Optional[str] = None
    toggled_by: str
    toggled_at: datetime
