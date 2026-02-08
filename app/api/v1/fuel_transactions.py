from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.fuel_transaction import FuelTransaction
from app.schemas.fuel_transaction import FuelTransactionOut

router = APIRouter()

@router.get("/fuel-transactions", response_model=list[FuelTransactionOut])
def list_fuel_transactions(db: Session = Depends(get_db)):
    return db.query(FuelTransaction).order_by(FuelTransaction.id.desc()).all()
