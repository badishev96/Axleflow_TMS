from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.ifta_return_draft import IFTAReturnDraft
from app.schemas.ifta_return_draft import IFTAReturnDraftCreate, IFTAReturnDraftOut

router = APIRouter()

@router.get("/ifta-return-drafts", response_model=list[IFTAReturnDraftOut])
def list_ifta_return_drafts(db: Session = Depends(get_db)):
    return db.query(IFTAReturnDraft).order_by(IFTAReturnDraft.id.desc()).all()

@router.post("/ifta-return-drafts", response_model=IFTAReturnDraftOut)
def create_ifta_return_draft(payload: IFTAReturnDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rd = IFTAReturnDraft(**payload.model_dump())
    db.add(rd)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="IFTAReturnDraft already exists for this draft_id")
    db.refresh(rd)
    return rd
