from pydantic import BaseModel
from datetime import datetime

class TruckCreate(BaseModel):
    company_id: int
    truck_number: str
    primary_driver_id: int | None = None
    secondary_driver_id: int | None = None
    current_location: str | None = None
    eta: str | None = None

class TruckUpdate(BaseModel):
    company_id: int | None = None
    truck_number: str | None = None
    primary_driver_id: int | None = None
    secondary_driver_id: int | None = None
    current_location: str | None = None
    eta: str | None = None

class TruckOut(TruckCreate):
    id: int
    created_at: datetime
