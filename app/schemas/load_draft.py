from pydantic import BaseModel
from datetime import datetime

class LoadDraftBase(BaseModel):
    draft_id: int

    load_number: str | None = None

    broker_company_name: str | None = None
    broker_address: str | None = None
    broker_mc_number: str | None = None
    broker_agent_name: str | None = None
    broker_agent_phone: str | None = None
    broker_agent_email: str | None = None

    pickup_company_name: str | None = None
    pickup_address: str | None = None
    pickup_hours: str | None = None
    pickup_contact_name: str | None = None
    pickup_contact_phone: str | None = None

    delivery_company_name: str | None = None
    delivery_address: str | None = None
    delivery_hours: str | None = None
    delivery_contact_name: str | None = None
    delivery_contact_phone: str | None = None

    pickup_datetime: datetime | None = None
    delivery_datetime: datetime | None = None

    rate_amount: float | None = None
    rate_type: str | None = None

    commodity: str | None = None
    description: str | None = None
    weight: str | None = None
    dimensions: str | None = None

    load_notes: str | None = None

class LoadDraftCreate(LoadDraftBase):
    pass

class LoadDraftOut(LoadDraftBase):
    id: int
