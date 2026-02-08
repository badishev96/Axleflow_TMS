from pydantic import BaseModel
from datetime import datetime

class ExpenseDraftBase(BaseModel):
    draft_id: int

    expense_date: datetime | None = None
    amount: float | None = None
    currency: str = "USD"

    expense_category: str | None = None

    anchor_type: str | None = None
    anchor_id: int | None = None

    vendor_name: str | None = None
    reference_number: str | None = None

    notes: str | None = None

class ExpenseDraftCreate(ExpenseDraftBase):
    pass

class ExpenseDraftOut(ExpenseDraftBase):
    id: int
