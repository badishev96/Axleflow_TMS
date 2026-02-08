from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.draft import Draft
from app.schemas.draft import DraftCreate, DraftOut

router = APIRouter()

@router.get("/drafts", response_model=list[DraftOut])
def list_drafts(db: Session = Depends(get_db)):
    return db.query(Draft).order_by(Draft.id.desc()).all()

@router.post("/drafts", response_model=DraftOut)
def create_draft(payload: DraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    draft = Draft(
        company_id=payload.company_id,
        draft_type=payload.draft_type.strip().lower(),
        status="draft",
        created_by_user_id=payload.created_by_user_id,
        updated_by_user_id=payload.created_by_user_id,
        source=payload.source.strip().lower(),
        source_ref=payload.source_ref,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft
