from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.session import get_db
from app.models.draft import Draft

from app.models.load_draft import LoadDraft
from app.models.expense_draft import ExpenseDraft
from app.models.fuel_transaction_draft import FuelTransactionDraft
from app.models.inventory_event_draft import InventoryEventDraft

from app.models.ifta_return_draft import IFTAReturnDraft
from app.models.ifta_return_state_line_draft import IFTAReturnStateLineDraft
from app.models.ifta_tax_rate import IFTATaxRate

router = APIRouter()

def review_draft(draft_id: int, db: Session):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.status in ["submitted", "discarded"]:
        raise HTTPException(status_code=409, detail="Draft cannot be reviewed")

    if draft.draft_type != "ifta":
        raise HTTPException(status_code=409, detail="Not an IFTA draft")

    ifta = db.query(IFTAReturnDraft).filter(IFTAReturnDraft.draft_id == draft.id).first()
    if not ifta:
        raise HTTPException(status_code=422, detail="IFTA return draft missing")

    if not ifta.quarter:
        raise HTTPException(status_code=422, detail="Quarter is required")

    lines = db.query(IFTAReturnStateLineDraft).filter(
        IFTAReturnStateLineDraft.ifta_return_draft_id == ifta.id
    ).all()

    if not lines:
        raise HTTPException(status_code=422, detail="At least one state line is required")

    total_miles = Decimal("0")
    total_gallons = Decimal("0")
    total_tax = Decimal("0")
    total_credits = Decimal("0")

    for line in lines:
        total_miles += Decimal(line.miles)
        total_gallons += Decimal(line.gallons)
        total_credits += Decimal(line.credit)

        rate = db.query(IFTATaxRate).filter(
            IFTATaxRate.company_id == draft.company_id,
            IFTATaxRate.state == line.state,
            IFTATaxRate.quarter == ifta.quarter
        ).first()

        if not rate:
            raise HTTPException(
                status_code=422,
                detail=f"Missing tax rate for {line.state} {ifta.quarter}"
            )

        state_tax = Decimal(line.gallons) * Decimal(rate.tax_rate_per_gallon)
        total_tax += state_tax

    mpg = (total_miles / total_gallons) if total_gallons > 0 else Decimal("0")

    ifta.total_miles = total_miles
    ifta.total_gallons = total_gallons
    ifta.mpg = mpg
    ifta.total_tax_due = total_tax
    ifta.total_credits = total_credits
    ifta.net_due = total_tax - total_credits

    draft.status = "reviewing"

    db.commit()
    return {
        "status": "ok",
        "draft_id": draft.id,
        "mpg": float(mpg),
        "net_due": float(ifta.net_due)
    }

@router.post("/drafts/{draft_id}/review")
def review_router(draft_id: int, db: Session = Depends(get_db)):
    return review_draft(draft_id, db)
