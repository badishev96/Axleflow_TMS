from pydantic import BaseModel
from datetime import datetime

class InventoryEventOut(BaseModel):
    id: int
    company_id: int
    item_id: int
    quantity_delta: int
    unit_cost: float
    event_type: str
    from_location_id: int | None
    to_location_id: int | None
    linked_entity_type: str | None
    linked_entity_id: int | None
    event_timestamp: datetime
    notes: str | None
    created_at: datetime
