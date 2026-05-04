from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from .database import SessionLocal
from .orm import EvalRun, PromptResult as PromptResultORM

if TYPE_CHECKING:
    from runner.models import PromptResult


class RunRepository:
    def __init__(self, db: Session | None = None):
        self._db = db or SessionLocal()
        self._owns_session = db is None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if self._owns_session:
            self._db.close()

    def create_run(self, run_id: str, model: str, started_at: datetime) -> EvalRun:
        run = EvalRun(id=run_id, model=model, started_at=started_at)
        self._db.add(run)
        self._db.commit()
        return run

    def save_result(self, run_id: str, result: "PromptResult") -> None:
        row = PromptResultORM(
            run_id=run_id,
            prompt_id=result.prompt_id,
            category=result.category,
            severity=result.severity,
            expected_behavior=result.expected_behavior,
            model_response=result.model_response,
            verdict=result.verdict,
            reason=result.reason,
            latency_ms=result.latency_ms,
        )
        self._db.add(row)
        # Update run counters inline
        run = self._db.get(EvalRun, run_id)
        if run:
            run.total += 1
            if result.verdict == "pass":
                run.passed += 1
            elif result.verdict == "fail":
                run.failed += 1
            else:
                run.errors += 1
        self._db.commit()

    def complete_run(self, run_id: str, completed_at: datetime) -> None:
        run = self._db.get(EvalRun, run_id)
        if run:
            run.completed_at = completed_at
            self._db.commit()

    def list_runs(self, limit: int = 20) -> list[EvalRun]:
        return (
            self._db.query(EvalRun)
            .order_by(EvalRun.started_at.desc())
            .limit(limit)
            .all()
        )

    def get_run(self, run_id: str) -> EvalRun | None:
        return self._db.get(EvalRun, run_id)

    def get_results_for_run(self, run_id: str) -> list[PromptResultORM]:
        return (
            self._db.query(PromptResultORM)
            .filter(PromptResultORM.run_id == run_id)
            .all()
        )

    def category_summary_for_run(self, run_id: str) -> list[dict]:
        results = self.get_results_for_run(run_id)
        by_cat: dict[str, dict] = {}
        for r in results:
            cat = by_cat.setdefault(r.category, {"category": r.category, "total": 0, "passed": 0, "failed": 0, "errors": 0})
            cat["total"] += 1
            if r.verdict == "pass":
                cat["passed"] += 1
            elif r.verdict == "fail":
                cat["failed"] += 1
            else:
                cat["errors"] += 1
        for cat in by_cat.values():
            eligible = cat["total"] - cat["errors"]
            cat["pass_rate"] = round(cat["passed"] / eligible, 4) if eligible else 0.0
        return list(by_cat.values())
