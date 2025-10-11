"""Quality assurance contracts."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class QAChecklistRef(BaseModel):
    template: str
    version: Optional[str] = None


class Defect(BaseModel):
    code: str
    description: Optional[str] = None
    severity: str = Field(..., description="low/medium/high/critical")


class QAOutcome(BaseModel):
    repair_order: str
    checklist: QAChecklistRef
    passed: bool
    inspected_by: str
    inspected_at: datetime
    notes: Optional[str] = None
    defects: List[Defect] = Field(default_factory=list)
