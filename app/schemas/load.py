from pydantic import BaseModel
from datetime import datetime

class LoadOut(BaseModel):
    id: int
    company_id: int
    truck_id: int | None
    dispatcher_id: int | None

    loaded_miles: float | None
    deadhead_miles: float | None
    total_miles: float | None

    load_number: str | None

    broker_company_name: str | None
    broker_address: str | None
    broker_mc_number: str | None
    broker_agent_name: str | None
    broker_agent_phone: str | None
    broker_agent_email: str | None

    pickup_company_name: str | None
    pickup_address: str | None
    pickup_hours: str | None
    pickup_contact_name: str | None
    pickup_contact_phone: str | None

    delivery_company_name: str | None
    delivery_address: str | None
    delivery_hours: str | None
    delivery_contact_name: str | None
    delivery_contact_phone: str | None

    pickup_datetime: datetime | None
    delivery_datetime: datetime | None

    rate_amount: float | None
    rate_type: str | None

    commodity: str | None
    description: str | None
    weight: str | None
    dimensions: str | None

    load_notes: str | None
    created_at: datetime
