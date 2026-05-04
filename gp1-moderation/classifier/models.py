from pydantic import BaseModel, Field
from shared.taxonomy import HarmCategory, Severity


class ModerationRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10_000, description="Text to moderate")
    context: str | None = Field(None, description="Optional surrounding context (e.g. platform, prior messages)")


class CategoryResult(BaseModel):
    category: HarmCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class ModerationResult(BaseModel):
    flagged: bool
    primary_category: HarmCategory
    severity: Severity
    categories: list[CategoryResult]
    summary: str
    content_hash: str


class ModerationResponse(BaseModel):
    request_id: str
    result: ModerationResult
    model_used: str
    latency_ms: float
