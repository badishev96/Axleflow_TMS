from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.inventory_item import InventoryItem
from app.schemas.inventory_item import InventoryItemCreate, InventoryItemOut

router = APIRouter()

@router.get("/inventory-items", response_model=list[InventoryItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(InventoryItem).order_by(InventoryItem.id.desc()).all()

@router.post("/inventory-items", response_model=InventoryItemOut)
def create_item(payload: InventoryItemCreate, db: Session = Depends(get_db)):
    item = InventoryItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
