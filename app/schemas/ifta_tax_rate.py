from pydantic import BaseModel
from datetime import datetime

class IFTATaxRateCreate(BaseModel):
    company_id: int
    state: str
    quarter: str
    tax_rate_per_gallon: float

class IFTATaxRateOut(IFTATaxRateCreate):
    id: int
    updated_at: datetime
