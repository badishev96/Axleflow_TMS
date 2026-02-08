from pydantic import BaseModel
from datetime import datetime

class InventoryEventDraftBase(BaseModel):
    draft_id: int

    item_id: int | None = None
    quantity_delta: int | None = None
    unit_cost: float | None = None

    event_type: str | None = None
    from_location_id: int | None = None
    to_location_id: int | None = None

    linked_entity_type: str | None = None
    linked_entity_id: int | None = None

    event_timestamp: datetime | None = None
    notes: str | None = None

class InventoryEventDraftCreate(InventoryEventDraftBase):
    pass

class InventoryEventDraftOut(InventoryEventDraftBase):
    id: int
