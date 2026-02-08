from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.settlement import Settlement
from app.schemas.settlement import SettlementOut

router = APIRouter()

@router.get("/settlements", response_model=list[SettlementOut])
def list_settlements(db: Session = Depends(get_db)):
    return db.query(Settlement).order_by(Settlement.id.desc()).all()
