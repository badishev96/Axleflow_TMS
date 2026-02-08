from pydantic import BaseModel
from datetime import datetime

class InventoryLocationCreate(BaseModel):
    company_id: int
    location_type: str
    location_ref_id: int | None = None
    name: str

class InventoryLocationOut(InventoryLocationCreate):
    id: int
    created_at: datetime
