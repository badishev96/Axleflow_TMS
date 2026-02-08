from pydantic import BaseModel
from datetime import datetime

class ExpenseOut(BaseModel):
    id: int
    company_id: int

    expense_date: datetime
    amount: float
    currency: str

    expense_category: str
    anchor_type: str
    anchor_id: int

    vendor_name: str
    reference_number: str | None
    notes: str | None

    created_at: datetime
