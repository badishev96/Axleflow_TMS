from pydantic import BaseModel

class IFTAStateLineDraftCreate(BaseModel):
    ifta_return_draft_id: int
    state: str
    miles: float = 0
    gallons: float = 0
    credit: float = 0

class IFTAStateLineDraftOut(IFTAStateLineDraftCreate):
    id: int
