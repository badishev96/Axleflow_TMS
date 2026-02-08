from pydantic import BaseModel
from datetime import datetime

class IFTAReturnDraftCreate(BaseModel):
    draft_id: int
    quarter: str | None = None
    status_note: str | None = None

class IFTAReturnDraftOut(IFTAReturnDraftCreate):
    id: int
    total_miles: float | None = None
    total_gallons: float | None = None
    mpg: float | None = None
    total_tax_due: float | None = None
    total_credits: float | None = None
    net_due: float | None = None
    created_at: datetime
