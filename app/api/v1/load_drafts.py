from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.load_draft import LoadDraft
from app.schemas.load_draft import LoadDraftCreate, LoadDraftOut

router = APIRouter()

@router.get("/load-drafts", response_model=list[LoadDraftOut])
def list_load_drafts(db: Session = Depends(get_db)):
    return db.query(LoadDraft).order_by(LoadDraft.id.desc()).all()

@router.post("/load-drafts", response_model=LoadDraftOut)
def create_load_draft(payload: LoadDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ld = LoadDraft(**payload.model_dump())
    db.add(ld)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="LoadDraft already exists for this draft_id")
    db.refresh(ld)
    return ld

@router.patch("/load-drafts/{draft_id}", response_model=LoadDraftOut)
def update_load_draft(draft_id: int, payload: LoadDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ld = db.query(LoadDraft).filter(LoadDraft.draft_id == draft_id).first()
    if not ld:
        raise HTTPException(status_code=404, detail="LoadDraft not found for this draft_id")

    data = payload.model_dump(exclude_unset=True)
    data.pop("draft_id", None)

    for k, v in data.items():
        setattr(ld, k, v)

    db.commit()
    db.refresh(ld)
    return ld
