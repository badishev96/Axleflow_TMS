from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.settlement_draft import SettlementDraft
from app.schemas.settlement_draft import SettlementDraftCreate, SettlementDraftOut

router = APIRouter()

@router.get("/settlement-drafts", response_model=list[SettlementDraftOut])
def list_settlement_drafts(db: Session = Depends(get_db)):
    return db.query(SettlementDraft).order_by(SettlementDraft.id.desc()).all()

@router.post("/settlement-drafts", response_model=SettlementDraftOut)
def create_settlement_draft(payload: SettlementDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sd = SettlementDraft(**payload.model_dump())
    db.add(sd)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="SettlementDraft already exists for this draft_id")
    db.refresh(sd)
    return sd

@router.patch("/settlement-drafts/{draft_id}", response_model=SettlementDraftOut)
def update_settlement_draft(draft_id: int, payload: SettlementDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sd = db.query(SettlementDraft).filter(SettlementDraft.draft_id == draft_id).first()
    if not sd:
        raise HTTPException(status_code=404, detail="SettlementDraft not found for this draft_id")

    data = payload.model_dump(exclude_unset=True)
    data.pop("draft_id", None)

    for k, v in data.items():
        setattr(sd, k, v)

    db.commit()
    db.refresh(sd)
    return sd
