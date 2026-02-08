from pydantic import BaseModel
from datetime import datetime

class FuelTransactionOut(BaseModel):
    id: int
    company_id: int

    fuel_card_number: str | None
    transaction_datetime: datetime
    state: str

    gallons: float
    total_cost: float

    assignment_context_type: str | None
    assignment_context_id: int | None

    vendor_name: str | None
    notes: str | None

    created_at: datetime
