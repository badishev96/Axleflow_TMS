from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.expense_draft import ExpenseDraft
from app.schemas.expense_draft import ExpenseDraftCreate, ExpenseDraftOut

router = APIRouter()

@router.get("/expense-drafts", response_model=list[ExpenseDraftOut])
def list_expense_drafts(db: Session = Depends(get_db)):
    return db.query(ExpenseDraft).order_by(ExpenseDraft.id.desc()).all()

@router.post("/expense-drafts", response_model=ExpenseDraftOut)
def create_expense_draft(payload: ExpenseDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ed = ExpenseDraft(**payload.model_dump())
    db.add(ed)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="ExpenseDraft already exists for this draft_id")
    db.refresh(ed)
    return ed

@router.patch("/expense-drafts/{draft_id}", response_model=ExpenseDraftOut)
def update_expense_draft(draft_id: int, payload: ExpenseDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ed = db.query(ExpenseDraft).filter(ExpenseDraft.draft_id == draft_id).first()
    if not ed:
        raise HTTPException(status_code=404, detail="ExpenseDraft not found for this draft_id")

    data = payload.model_dump(exclude_unset=True)
    data.pop("draft_id", None)

    for k, v in data.items():
        setattr(ed, k, v)

    db.commit()
    db.refresh(ed)
    return ed
