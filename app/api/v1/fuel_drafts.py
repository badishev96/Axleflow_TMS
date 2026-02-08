from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.fuel_transaction_draft import FuelTransactionDraft
from app.schemas.fuel_draft import FuelDraftCreate, FuelDraftOut

router = APIRouter()

@router.get("/fuel-drafts", response_model=list[FuelDraftOut])
def list_fuel_drafts(db: Session = Depends(get_db)):
    return db.query(FuelTransactionDraft).order_by(FuelTransactionDraft.id.desc()).all()

@router.post("/fuel-drafts", response_model=FuelDraftOut)
def create_fuel_draft(payload: FuelDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fd = FuelTransactionDraft(**payload.model_dump())
    db.add(fd)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="FuelDraft already exists for this draft_id")
    db.refresh(fd)
    return fd

@router.patch("/fuel-drafts/{draft_id}", response_model=FuelDraftOut)
def update_fuel_draft(draft_id: int, payload: FuelDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fd = db.query(FuelTransactionDraft).filter(FuelTransactionDraft.draft_id == draft_id).first()
    if not fd:
        raise HTTPException(status_code=404, detail="FuelDraft not found for this draft_id")

    data = payload.model_dump(exclude_unset=True)
    data.pop("draft_id", None)

    for k, v in data.items():
        setattr(fd, k, v)

    db.commit()
    db.refresh(fd)
    return fd
