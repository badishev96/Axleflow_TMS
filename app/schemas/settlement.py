from pydantic import BaseModel
from datetime import datetime

class SettlementOut(BaseModel):
    id: int
    company_id: int
    load_id: int
    truck_id: int

    commission_basis: str
    total_commission_percent: float
    primary_driver_percent: float
    secondary_driver_percent: float

    commission_base_amount: float
    commission_pool_amount: float
    primary_driver_amount: float
    secondary_driver_amount: float

    notes: str | None
    created_at: datetime
