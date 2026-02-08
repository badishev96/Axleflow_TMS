from pydantic import BaseModel
from datetime import datetime

class SettlementDraftBase(BaseModel):
    draft_id: int
    load_id: int | None = None
    truck_id: int | None = None

    # NEW: driver IDs
    primary_driver_id: int | None = None
    secondary_driver_id: int | None = None

    commission_basis: str | None = None
    total_commission_percent: float | None = None

    primary_driver_percent: float | None = None
    secondary_driver_percent: float | None = None

    commission_base_amount: float | None = None
    commission_pool_amount: float | None = None
    primary_driver_amount: float | None = None
    secondary_driver_amount: float | None = None

    notes: str | None = None

class SettlementDraftCreate(SettlementDraftBase):
    pass

class SettlementDraftOut(SettlementDraftBase):
    id: int
    created_at: datetime
