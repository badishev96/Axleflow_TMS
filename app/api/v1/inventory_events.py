from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.inventory_event import InventoryEvent
from app.schemas.inventory_event import InventoryEventOut

router = APIRouter()

@router.get("/inventory-events", response_model=list[InventoryEventOut])
def list_inventory_events(db: Session = Depends(get_db)):
    return db.query(InventoryEvent).order_by(InventoryEvent.id.desc()).all()
