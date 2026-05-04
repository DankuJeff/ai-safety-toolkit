from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Verdict = Literal["pass", "fail", "error"]


class PromptResult(BaseModel):
    prompt_id: str
    category: str
    severity: int
    expected_behavior: str
    model_response: str
    verdict: Verdict
    reason: str
    latency_ms: float


class RunSummary(BaseModel):
    run_id: str
    model: str
    started_at: datetime
    completed_at: datetime | None
    total: int
    passed: int
    failed: int
    errors: int

    @property
    def pass_rate(self) -> float:
        eligible = self.total - self.errors
        return round(self.passed / eligible, 4) if eligible else 0.0


class CategorySummary(BaseModel):
    category: str
    total: int
    passed: int
    failed: int
    errors: int
    pass_rate: float = Field(..., ge=0.0, le=1.0)
