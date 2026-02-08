from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.inventory_location import InventoryLocation
from app.schemas.inventory_location import InventoryLocationCreate, InventoryLocationOut

router = APIRouter()

@router.get("/inventory-locations", response_model=list[InventoryLocationOut])
def list_locations(db: Session = Depends(get_db)):
    return db.query(InventoryLocation).order_by(InventoryLocation.id.desc()).all()

@router.post("/inventory-locations", response_model=InventoryLocationOut)
def create_location(payload: InventoryLocationCreate, db: Session = Depends(get_db)):
    loc = InventoryLocation(**payload.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc
