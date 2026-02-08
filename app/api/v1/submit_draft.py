from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.draft import Draft

from app.models.load_draft import LoadDraft
from app.models.load import Load

from app.models.expense_draft import ExpenseDraft
from app.models.expense import Expense

from app.models.fuel_transaction_draft import FuelTransactionDraft
from app.models.fuel_transaction import FuelTransaction
from app.models.fuel_card import FuelCard

from app.models.inventory_event_draft import InventoryEventDraft
from app.models.inventory_event import InventoryEvent

from app.models.settlement_draft import SettlementDraft
from app.models.settlement import Settlement

router = APIRouter()

@router.post("/drafts/{draft_id}/submit")
def submit_draft(draft_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # logged-in required

    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.status != "reviewing":
        raise HTTPException(status_code=409, detail="Draft must be in reviewing state to submit")

    if draft.draft_type == "load":
        ld = db.query(LoadDraft).filter(LoadDraft.draft_id == draft.id).first()
        if not ld:
            raise HTTPException(status_code=422, detail="LoadDraft missing")

        load = Load(company_id=draft.company_id, truck_id=None)
        load.load_number = ld.load_number

        load.broker_company_name = ld.broker_company_name
        load.broker_address = ld.broker_address
        load.broker_mc_number = ld.broker_mc_number
        load.broker_agent_name = ld.broker_agent_name
        load.broker_agent_phone = ld.broker_agent_phone
        load.broker_agent_email = ld.broker_agent_email

        load.pickup_company_name = ld.pickup_company_name
        load.pickup_address = ld.pickup_address
        load.pickup_hours = ld.pickup_hours
        load.pickup_contact_name = ld.pickup_contact_name
        load.pickup_contact_phone = ld.pickup_contact_phone

        load.delivery_company_name = ld.delivery_company_name
        load.delivery_address = ld.delivery_address
        load.delivery_hours = ld.delivery_hours
        load.delivery_contact_name = ld.delivery_contact_name
        load.delivery_contact_phone = ld.delivery_contact_phone

        load.pickup_datetime = ld.pickup_datetime
        load.delivery_datetime = ld.delivery_datetime

        load.rate_amount = ld.rate_amount
        load.rate_type = ld.rate_type

        load.commodity = ld.commodity
        load.description = ld.description
        load.weight = ld.weight
        load.dimensions = ld.dimensions
        load.load_notes = ld.load_notes

        db.add(load)
        db.flush()

        draft.status = "submitted"
        draft.submitted_by_user_id = draft.updated_by_user_id
        draft.submitted_at = datetime.utcnow()
        draft.target_entity_type = "load"
        draft.target_entity_id = load.id

        db.commit()
        return {"status": "submitted", "draft_type": "load", "entity_id": load.id}

    if draft.draft_type == "expense":
        ed = db.query(ExpenseDraft).filter(ExpenseDraft.draft_id == draft.id).first()
        if not ed:
            raise HTTPException(status_code=422, detail="ExpenseDraft missing")

        if not ed.expense_date or ed.amount is None or not ed.expense_category or not ed.anchor_type or ed.anchor_id is None or not ed.vendor_name:
            raise HTTPException(status_code=422, detail="ExpenseDraft incomplete")

        expense = Expense(
            company_id=draft.company_id,
            expense_date=ed.expense_date,
            amount=ed.amount,
            currency=ed.currency,
            expense_category=ed.expense_category,
            anchor_type=ed.anchor_type,
            anchor_id=ed.anchor_id,
            vendor_name=ed.vendor_name,
            reference_number=ed.reference_number,
            notes=ed.notes,
        )

        db.add(expense)
        db.flush()

        draft.status = "submitted"
        draft.submitted_by_user_id = draft.updated_by_user_id
        draft.submitted_at = datetime.utcnow()
        draft.target_entity_type = "expense"
        draft.target_entity_id = expense.id

        db.commit()
        return {"status": "submitted", "draft_type": "expense", "entity_id": expense.id}

    if draft.draft_type == "fuel":
        fd = db.query(FuelTransactionDraft).filter(FuelTransactionDraft.draft_id == draft.id).first()
        if not fd:
            raise HTTPException(status_code=422, detail="FuelDraft missing")

        if not fd.transaction_datetime or not fd.state or fd.gallons is None or fd.total_cost is None:
            raise HTTPException(status_code=422, detail="FuelDraft incomplete")

        assignment_type = fd.assignment_context_type
        assignment_id = fd.assignment_context_id

        if fd.fuel_card_number:
            card = db.query(FuelCard).filter(
                FuelCard.company_id == draft.company_id,
                FuelCard.card_number == fd.fuel_card_number
            ).first()
            if card and card.assigned_to_type and card.assigned_to_id:
                assignment_type = card.assigned_to_type
                assignment_id = card.assigned_to_id

        fuel_tx = FuelTransaction(
            company_id=draft.company_id,
            fuel_card_number=fd.fuel_card_number,
            transaction_datetime=fd.transaction_datetime,
            state=fd.state,
            gallons=fd.gallons,
            total_cost=fd.total_cost,
            assignment_context_type=assignment_type,
            assignment_context_id=assignment_id,
            vendor_name=fd.vendor_name,
            notes=fd.notes,
        )

        db.add(fuel_tx)
        db.flush()

        draft.status = "submitted"
        draft.submitted_by_user_id = draft.updated_by_user_id
        draft.submitted_at = datetime.utcnow()
        draft.target_entity_type = "fuel_transaction"
        draft.target_entity_id = fuel_tx.id

        db.commit()
        return {"status": "submitted", "draft_type": "fuel", "entity_id": fuel_tx.id}

    if draft.draft_type == "inventory":
        ie = db.query(InventoryEventDraft).filter(InventoryEventDraft.draft_id == draft.id).first()
        if not ie:
            raise HTTPException(status_code=422, detail="InventoryEventDraft missing")

        if ie.item_id is None or ie.quantity_delta is None or ie.unit_cost is None or not ie.event_type or not ie.event_timestamp:
            raise HTTPException(status_code=422, detail="InventoryEventDraft incomplete")

        inv_event = InventoryEvent(
            company_id=draft.company_id,
            item_id=ie.item_id,
            quantity_delta=ie.quantity_delta,
            unit_cost=ie.unit_cost,
            event_type=ie.event_type,
            from_location_id=ie.from_location_id,
            to_location_id=ie.to_location_id,
            linked_entity_type=ie.linked_entity_type,
            linked_entity_id=ie.linked_entity_id,
            event_timestamp=ie.event_timestamp,
            notes=ie.notes,
        )

        db.add(inv_event)
        db.flush()

        draft.status = "submitted"
        draft.submitted_by_user_id = draft.updated_by_user_id
        draft.submitted_at = datetime.utcnow()
        draft.target_entity_type = "inventory_event"
        draft.target_entity_id = inv_event.id

        db.commit()
        return {"status": "submitted", "draft_type": "inventory", "entity_id": inv_event.id}

    if draft.draft_type == "settlement":
        sd = db.query(SettlementDraft).filter(SettlementDraft.draft_id == draft.id).first()
        if not sd:
            raise HTTPException(status_code=422, detail="SettlementDraft missing")

        if sd.commission_base_amount is None or sd.commission_pool_amount is None or sd.primary_driver_amount is None:
            raise HTTPException(status_code=422, detail="SettlementDraft incomplete or not reviewed")

        settlement = Settlement(
            company_id=draft.company_id,
            load_id=sd.load_id,
            truck_id=sd.truck_id,
            primary_driver_id=sd.primary_driver_id,
            secondary_driver_id=sd.secondary_driver_id,
            commission_basis=sd.commission_basis,
            total_commission_percent=sd.total_commission_percent,
            primary_driver_percent=sd.primary_driver_percent,
            secondary_driver_percent=sd.secondary_driver_percent or 0,
            commission_base_amount=sd.commission_base_amount,
            commission_pool_amount=sd.commission_pool_amount,
            primary_driver_amount=sd.primary_driver_amount,
            secondary_driver_amount=sd.secondary_driver_amount or 0,
            notes=sd.notes,
        )

        db.add(settlement)
        db.flush()

        draft.status = "submitted"
        draft.submitted_by_user_id = draft.updated_by_user_id
        draft.submitted_at = datetime.utcnow()
        draft.target_entity_type = "settlement"
        draft.target_entity_id = settlement.id

        db.commit()
        return {"status": "submitted", "draft_type": "settlement", "entity_id": settlement.id}

    raise HTTPException(status_code=409, detail="Unsupported draft type for submit")
