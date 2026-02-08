from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.inventory_event_draft import InventoryEventDraft
from app.schemas.inventory_event_draft import InventoryEventDraftCreate, InventoryEventDraftOut

router = APIRouter()

@router.get("/inventory-event-drafts", response_model=list[InventoryEventDraftOut])
def list_inventory_event_drafts(db: Session = Depends(get_db)):
    return db.query(InventoryEventDraft).order_by(InventoryEventDraft.id.desc()).all()

@router.post("/inventory-event-drafts", response_model=InventoryEventDraftOut)
def create_inventory_event_draft(payload: InventoryEventDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ed = InventoryEventDraft(**payload.model_dump())
    db.add(ed)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="InventoryEventDraft already exists for this draft_id")
    db.refresh(ed)
    return ed

@router.patch("/inventory-event-drafts/{draft_id}", response_model=InventoryEventDraftOut)
def update_inventory_event_draft(draft_id: int, payload: InventoryEventDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ed = db.query(InventoryEventDraft).filter(InventoryEventDraft.draft_id == draft_id).first()
    if not ed:
        raise HTTPException(status_code=404, detail="InventoryEventDraft not found for this draft_id")

    data = payload.model_dump(exclude_unset=True)
    data.pop("draft_id", None)

    for k, v in data.items():
        setattr(ed, k, v)

    db.commit()
    db.refresh(ed)
    return ed
