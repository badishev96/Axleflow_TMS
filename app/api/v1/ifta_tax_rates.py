from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.ifta_tax_rate import IFTATaxRate
from app.schemas.ifta_tax_rate import IFTATaxRateCreate, IFTATaxRateOut

router = APIRouter()

@router.get("/ifta-tax-rates", response_model=list[IFTATaxRateOut])
def list_rates(db: Session = Depends(get_db)):
    return db.query(IFTATaxRate).order_by(IFTATaxRate.id.desc()).all()

@router.post("/ifta-tax-rates", response_model=IFTATaxRateOut)
def create_rate(payload: IFTATaxRateCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = IFTATaxRate(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.patch("/ifta-tax-rates/{rate_id}", response_model=IFTATaxRateOut)
def update_rate(rate_id: int, payload: IFTATaxRateCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = db.query(IFTATaxRate).filter(IFTATaxRate.id == rate_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rate not found")

    r.company_id = payload.company_id
    r.state = payload.state
    r.quarter = payload.quarter
    r.tax_rate_per_gallon = payload.tax_rate_per_gallon

    db.commit()
    db.refresh(r)
    return r
