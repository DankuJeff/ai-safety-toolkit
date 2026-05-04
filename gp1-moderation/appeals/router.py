from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .database import get_db
from .orm import Appeal
from .schemas import AppealCreate, AppealList, AppealRead, AppealUpdate

router = APIRouter(prefix="/api/v1/appeals", tags=["appeals"])


@router.post("/", response_model=AppealRead, status_code=201)
def create_appeal(payload: AppealCreate, db: Session = Depends(get_db)):
    appeal = Appeal(**payload.model_dump())
    db.add(appeal)
    db.commit()
    db.refresh(appeal)
    return appeal


@router.get("/", response_model=AppealList)
def list_appeals(
    status: str | None = Query(None, pattern="^(pending|approved|rejected)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Appeal).filter(Appeal.deleted_at.is_(None))
    if status:
        query = query.filter(Appeal.status == status)
    total = query.count()
    items = query.order_by(Appeal.created_at.desc()).offset(offset).limit(limit).all()
    return AppealList(items=items, total=total)


@router.get("/{appeal_id}", response_model=AppealRead)
def get_appeal(appeal_id: str, db: Session = Depends(get_db)):
    appeal = db.query(Appeal).filter(Appeal.id == appeal_id, Appeal.deleted_at.is_(None)).first()
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")
    return appeal


@router.patch("/{appeal_id}", response_model=AppealRead)
def update_appeal(appeal_id: str, payload: AppealUpdate, db: Session = Depends(get_db)):
    appeal = db.query(Appeal).filter(Appeal.id == appeal_id, Appeal.deleted_at.is_(None)).first()
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")
    if appeal.status != "pending":
        raise HTTPException(status_code=409, detail=f"Appeal already resolved as '{appeal.status}'")
    appeal.status = payload.status
    appeal.reviewer_notes = payload.reviewer_notes
    appeal.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(appeal)
    return appeal


@router.delete("/{appeal_id}", status_code=204)
def delete_appeal(appeal_id: str, db: Session = Depends(get_db)):
    appeal = db.query(Appeal).filter(Appeal.id == appeal_id, Appeal.deleted_at.is_(None)).first()
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")
    appeal.deleted_at = datetime.now(timezone.utc)
    db.commit()
