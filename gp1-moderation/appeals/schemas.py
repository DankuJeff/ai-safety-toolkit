from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from shared.taxonomy import HarmCategory, Severity


class AppealCreate(BaseModel):
    request_id: str
    content_hash: str
    original_content: str = Field(..., max_length=10_000)
    flagged_category: HarmCategory
    severity: Severity
    appeal_reason: str = Field(..., min_length=10, max_length=2_000)


class AppealUpdate(BaseModel):
    status: Literal["approved", "rejected"]
    reviewer_notes: str | None = None


class AppealRead(BaseModel):
    id: str
    request_id: str
    content_hash: str
    original_content: str
    flagged_category: HarmCategory
    severity: Severity
    appeal_reason: str
    status: Literal["pending", "approved", "rejected"]
    reviewer_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppealList(BaseModel):
    items: list[AppealRead]
    total: int
