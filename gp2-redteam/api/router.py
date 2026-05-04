from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from tracker.repository import RunRepository
from tracker.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1", tags=["redteam"])


def get_repo(db: Session = Depends(get_db)) -> RunRepository:
    return RunRepository(db)


class RunRead(BaseModel):
    run_id: str
    model: str
    started_at: str
    completed_at: str | None
    total: int
    passed: int
    failed: int
    errors: int
    pass_rate: float

    model_config = {"from_attributes": True}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/runs")
def list_runs(limit: int = 20, repo: RunRepository = Depends(get_repo)):
    runs = repo.list_runs(limit)
    return [
        {
            "run_id": r.id,
            "model": r.model,
            "started_at": r.started_at.isoformat(),
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "total": r.total,
            "passed": r.passed,
            "failed": r.failed,
            "errors": r.errors,
            "pass_rate": round(r.passed / (r.total - r.errors), 4) if (r.total - r.errors) > 0 else 0.0,
        }
        for r in runs
    ]


@router.get("/runs/latest")
def latest_run(repo: RunRepository = Depends(get_repo)):
    runs = repo.list_runs(1)
    if not runs:
        raise HTTPException(status_code=404, detail="No runs found")
    r = runs[0]
    return {
        "run_id": r.id,
        "model": r.model,
        "started_at": r.started_at.isoformat(),
        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        "total": r.total,
        "passed": r.passed,
        "failed": r.failed,
        "errors": r.errors,
        "pass_rate": round(r.passed / (r.total - r.errors), 4) if (r.total - r.errors) > 0 else 0.0,
    }


@router.get("/runs/{run_id}/summary")
def run_summary(run_id: str, repo: RunRepository = Depends(get_repo)):
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    categories = repo.category_summary_for_run(run_id)
    return {
        "run_id": run.id,
        "model": run.model,
        "started_at": run.started_at.isoformat(),
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "total": run.total,
        "passed": run.passed,
        "failed": run.failed,
        "errors": run.errors,
        "pass_rate": round(run.passed / (run.total - run.errors), 4) if (run.total - run.errors) > 0 else 0.0,
        "categories": categories,
    }


@router.get("/runs/{run_id}/results")
def run_results(run_id: str, repo: RunRepository = Depends(get_repo)):
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    results = repo.get_results_for_run(run_id)
    return [
        {
            "prompt_id": r.prompt_id,
            "category": r.category,
            "severity": r.severity,
            "expected_behavior": r.expected_behavior,
            "verdict": r.verdict,
            "reason": r.reason,
            "latency_ms": r.latency_ms,
        }
        for r in results
    ]


@router.get("/regression")
def regression(limit: int = 10, repo: RunRepository = Depends(get_repo)):
    """Pass rates per run over time — powers the regression trend chart."""
    runs = repo.list_runs(limit)
    return [
        {
            "run_id": r.id[:8],
            "model": r.model,
            "date": r.started_at.strftime("%H:%M"),
            "pass_rate": round(r.passed / (r.total - r.errors) * 100, 1) if (r.total - r.errors) > 0 else 0.0,
            "total": r.total,
        }
        for r in reversed(runs)
    ]
