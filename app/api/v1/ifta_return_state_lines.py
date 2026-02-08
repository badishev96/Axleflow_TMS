from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.ifta_return_state_line_draft import IFTAReturnStateLineDraft
from app.schemas.ifta_return_state_line_draft import IFTAStateLineDraftCreate, IFTAStateLineDraftOut

router = APIRouter()

@router.get("/ifta-return-state-lines", response_model=list[IFTAStateLineDraftOut])
def list_state_lines(db: Session = Depends(get_db)):
    return db.query(IFTAReturnStateLineDraft).order_by(IFTAReturnStateLineDraft.id.desc()).all()

@router.post("/ifta-return-state-lines", response_model=IFTAStateLineDraftOut)
def create_state_line(payload: IFTAStateLineDraftCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    line = IFTAReturnStateLineDraft(**payload.model_dump())
    db.add(line)
    db.commit()
    db.refresh(line)
    return line
