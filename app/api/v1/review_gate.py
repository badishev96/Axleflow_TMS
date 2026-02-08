from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.draft import Draft
from app.models.load_draft import LoadDraft
from app.models.expense_draft import ExpenseDraft
from app.models.fuel_transaction_draft import FuelTransactionDraft
from app.models.inventory_event_draft import InventoryEventDraft

from app.models.settlement_draft import SettlementDraft
from app.models.load import Load
from app.models.expense import Expense
from app.models.truck import Truck

router = APIRouter()

def validate_load_draft(ld: LoadDraft):
    missing = []
    if not ld.pickup_address and not ld.pickup_location:
        missing.append("pickup_address")
    if not ld.delivery_address and not ld.delivery_location:
        missing.append("delivery_address")
    if not ld.pickup_datetime:
        missing.append("pickup_datetime")
    if not ld.delivery_datetime:
        missing.append("delivery_datetime")
    if ld.rate_amount is None:
        missing.append("rate_amount")
    if not ld.rate_type:
        missing.append("rate_type")
    return missing

def validate_expense_draft(ed: ExpenseDraft):
    missing = []
    if not ed.expense_date:
        missing.append("expense_date")
    if ed.amount is None:
        missing.append("amount")
    if not ed.expense_category:
        missing.append("expense_category")
    if not ed.anchor_type:
        missing.append("anchor_type")
    if ed.anchor_id is None:
        missing.append("anchor_id")
    if not ed.vendor_name:
        missing.append("vendor_name")
    return missing

def validate_fuel_draft(fd: FuelTransactionDraft):
    missing = []
    if not fd.transaction_datetime:
        missing.append("transaction_datetime")
    if not fd.state:
        missing.append("state")
    if fd.gallons is None:
        missing.append("gallons")
    if fd.total_cost is None:
        missing.append("total_cost")
    return missing

def validate_inventory_draft(ie: InventoryEventDraft):
    missing = []
    if ie.item_id is None:
        missing.append("item_id")
    if ie.quantity_delta is None:
        missing.append("quantity_delta")
    if ie.unit_cost is None:
        missing.append("unit_cost")
    if not ie.event_type:
        missing.append("event_type")
    if not ie.event_timestamp:
        missing.append("event_timestamp")
    if ie.event_type == "moved":
        if ie.from_location_id is None:
            missing.append("from_location_id")
        if ie.to_location_id is None:
            missing.append("to_location_id")
    return missing

def validate_settlement(sd: SettlementDraft):
    missing = []
    if sd.load_id is None:
        missing.append("load_id")
    if not sd.commission_basis:
        missing.append("commission_basis")
    if sd.total_commission_percent is None:
        missing.append("total_commission_percent")
    if sd.primary_driver_percent is None:
        missing.append("primary_driver_percent")
    return missing

@router.post("/drafts/{draft_id}/review")
def review_draft(draft_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # logged-in required (current_user dependency enforces session)

    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.status in ["submitted", "discarded"]:
        raise HTTPException(status_code=409, detail=f"Draft is {draft.status} and cannot be reviewed")

    if draft.draft_type == "load":
        ld = db.query(LoadDraft).filter(LoadDraft.draft_id == draft.id).first()
        if not ld:
            raise HTTPException(status_code=422, detail={"missing_required_fields": ["load_draft_record_missing"]})
        missing = validate_load_draft(ld)
        if missing:
            raise HTTPException(status_code=422, detail={"missing_required_fields": missing})

    elif draft.draft_type == "expense":
        ed = db.query(ExpenseDraft).filter(ExpenseDraft.draft_id == draft.id).first()
        if not ed:
            raise HTTPException(status_code=422, detail={"missing_required_fields": ["expense_draft_record_missing"]})
        missing = validate_expense_draft(ed)
        if missing:
            raise HTTPException(status_code=422, detail={"missing_required_fields": missing})

    elif draft.draft_type == "fuel":
        fd = db.query(FuelTransactionDraft).filter(FuelTransactionDraft.draft_id == draft.id).first()
        if not fd:
            raise HTTPException(status_code=422, detail={"missing_required_fields": ["fuel_draft_record_missing"]})
        missing = validate_fuel_draft(fd)
        if missing:
            raise HTTPException(status_code=422, detail={"missing_required_fields": missing})

    elif draft.draft_type == "inventory":
        ie = db.query(InventoryEventDraft).filter(InventoryEventDraft.draft_id == draft.id).first()
        if not ie:
            raise HTTPException(status_code=422, detail={"missing_required_fields": ["inventory_event_draft_record_missing"]})
        missing = validate_inventory_draft(ie)
        if missing:
            raise HTTPException(status_code=422, detail={"missing_required_fields": missing})

    elif draft.draft_type == "settlement":
        sd = db.query(SettlementDraft).filter(SettlementDraft.draft_id == draft.id).first()
        if not sd:
            raise HTTPException(status_code=422, detail={"missing_required_fields": ["settlement_draft_record_missing"]})

        missing = validate_settlement(sd)
        if missing:
            raise HTTPException(status_code=422, detail={"missing_required_fields": missing})

        load = db.query(Load).filter(Load.id == sd.load_id).first()
        if not load:
            raise HTTPException(status_code=422, detail="Load not found for settlement")

        truck_id = sd.truck_id or load.truck_id
        if truck_id is None:
            raise HTTPException(status_code=422, detail="truck_id is required (assign load to a truck first)")

        truck = db.query(Truck).filter(Truck.id == truck_id).first()
        if not truck:
            raise HTTPException(status_code=422, detail="Truck not found for settlement")

        sd.truck_id = truck_id
        sd.primary_driver_id = truck.primary_driver_id
        sd.secondary_driver_id = truck.secondary_driver_id

        basis = sd.commission_basis.lower()
        if basis not in ["gross", "net"]:
            raise HTTPException(status_code=422, detail="commission_basis must be 'gross' or 'net'")

        gross = Decimal(load.rate_amount or 0)
        net = gross

        if basis == "net":
            exp_sum = db.query(Expense).filter(
                Expense.anchor_type == "load",
                Expense.anchor_id == load.id
            ).all()
            total_exp = sum([Decimal(e.amount) for e in exp_sum]) if exp_sum else Decimal("0")
            net = gross - total_exp
            if net < 0:
                net = Decimal("0")

        base_amount = gross if basis == "gross" else net

        total_pct = Decimal(sd.total_commission_percent)
        p1_pct = Decimal(sd.primary_driver_percent)
        p2_pct = Decimal(sd.secondary_driver_percent or 0)

        # Auto-correct solo
        if sd.secondary_driver_id is None:
            p2_pct = Decimal("0")
            p1_pct = total_pct
            sd.secondary_driver_percent = float(p2_pct)
            sd.primary_driver_percent = float(p1_pct)

        if (p1_pct + p2_pct) != total_pct:
            raise HTTPException(status_code=422, detail="Driver split percents must equal total_commission_percent")

        pool_amount = (base_amount * total_pct) / Decimal("100")
        p1_amount = (base_amount * p1_pct) / Decimal("100")
        p2_amount = (base_amount * p2_pct) / Decimal("100")

        sd.commission_base_amount = base_amount
        sd.commission_pool_amount = pool_amount
        sd.primary_driver_amount = p1_amount
        sd.secondary_driver_amount = p2_amount

    else:
        raise HTTPException(status_code=409, detail="Unsupported draft_type for review gate")

    draft.status = "reviewing"
    db.commit()
    return {"status": "ok", "draft_id": draft.id, "draft_status": draft.status}
