from pydantic import BaseModel
from datetime import datetime

class FuelDraftBase(BaseModel):
    draft_id: int

    fuel_card_number: str | None = None
    transaction_datetime: datetime | None = None
    state: str | None = None

    gallons: float | None = None
    total_cost: float | None = None

    assignment_context_type: str | None = None
    assignment_context_id: int | None = None

    vendor_name: str | None = None
    notes: str | None = None

class FuelDraftCreate(FuelDraftBase):
    pass

class FuelDraftOut(FuelDraftBase):
    id: int
