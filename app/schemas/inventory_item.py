from pydantic import BaseModel
from datetime import datetime

class InventoryItemCreate(BaseModel):
    company_id: int
    name: str
    sku: str | None = None
    unit_cost: str | None = None

class InventoryItemOut(InventoryItemCreate):
    id: int
    created_at: datetime
