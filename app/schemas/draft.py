from pydantic import BaseModel
from datetime import datetime

class DraftCreate(BaseModel):
    company_id: int
    draft_type: str
    created_by_user_id: int
    source: str = "manual"
    source_ref: str | None = None

class DraftOut(BaseModel):
    id: int
    company_id: int
    draft_type: str
    status: str
    created_by_user_id: int
    created_at: datetime
    updated_by_user_id: int | None
    updated_at: datetime
    source: str
    source_ref: str | None
    version: int
