from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.fuel_card import FuelCard
from app.schemas.fuel_card import FuelCardCreate, FuelCardOut

router = APIRouter()

def validate_assignment(payload: FuelCardCreate):
    if payload.assigned_to_type is None and payload.assigned_to_id is None:
        return
    if payload.assigned_to_type not in ["driver", "truck"]:
        raise HTTPException(status_code=422, detail="assigned_to_type must be 'driver' or 'truck'")
    if payload.assigned_to_id is None:
        raise HTTPException(status_code=422, detail="assigned_to_id is required when assigned_to_type is set")

@router.get("/fuel-cards", response_model=list[FuelCardOut])
def list_fuel_cards(db: Session = Depends(get_db)):
    return db.query(FuelCard).order_by(FuelCard.id.desc()).all()

@router.post("/fuel-cards", response_model=FuelCardOut)
def create_fuel_card(payload: FuelCardCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_assignment(payload)
    card = FuelCard(**payload.model_dump())
    db.add(card)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Fuel card number already exists for this company")
    db.refresh(card)
    return card

@router.patch("/fuel-cards/{card_id}", response_model=FuelCardOut)
def update_fuel_card(card_id: int, payload: FuelCardCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_assignment(payload)
    card = db.query(FuelCard).filter(FuelCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Fuel card not found")

    card.company_id = payload.company_id
    card.vendor_name = payload.vendor_name
    card.card_number = payload.card_number
    card.assigned_to_type = payload.assigned_to_type
    card.assigned_to_id = payload.assigned_to_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Fuel card number already exists for this company")

    db.refresh(card)
    return card
