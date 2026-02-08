from pydantic import BaseModel
from datetime import datetime

class FuelCardCreate(BaseModel):
    company_id: int
    vendor_name: str
    card_number: str
    assigned_to_type: str | None = None
    assigned_to_id: int | None = None

class FuelCardOut(FuelCardCreate):
    id: int
    is_active: int
    created_at: datetime
