from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.truck import Truck
from app.schemas.truck import TruckCreate, TruckUpdate, TruckOut

router = APIRouter()

@router.get("/trucks", response_model=list[TruckOut])
def list_trucks(db: Session = Depends(get_db)):
    return db.query(Truck).order_by(Truck.id.desc()).all()

@router.post("/trucks", response_model=TruckOut)
def create_truck(payload: TruckCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    truck = Truck(**payload.model_dump())
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck

@router.patch("/trucks/{truck_id}", response_model=TruckOut)
def update_truck(truck_id: int, payload: TruckUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    data = payload.model_dump(exclude_unset=True)

    for k, v in data.items():
        setattr(truck, k, v)

    db.commit()
    db.refresh(truck)
    return truck
