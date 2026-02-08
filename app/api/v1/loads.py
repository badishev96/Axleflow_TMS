from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.session_auth import get_current_user
from app.models.user import User

from app.models.load import Load
from app.schemas.load import LoadOut

router = APIRouter()

@router.get("/loads", response_model=list[LoadOut])
def list_loads(db: Session = Depends(get_db)):
    return db.query(Load).order_by(Load.id.desc()).all()

@router.patch("/loads/{load_id}", response_model=LoadOut)
def update_load(load_id: int, payload: dict, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    load = db.query(Load).filter(Load.id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")

    # ✅ allow dispatcher_id now
    allowed = {"truck_id", "dispatcher_id", "loaded_miles", "deadhead_miles", "total_miles"}
    for k in payload.keys():
        if k not in allowed:
            raise HTTPException(status_code=422, detail=f"Field not allowed: {k}")

    if "truck_id" in payload:
        load.truck_id = payload["truck_id"]

    if "dispatcher_id" in payload:
        load.dispatcher_id = payload["dispatcher_id"]

    if "loaded_miles" in payload:
        load.loaded_miles = payload["loaded_miles"]

    if "deadhead_miles" in payload:
        load.deadhead_miles = payload["deadhead_miles"]

    if "total_miles" in payload:
        load.total_miles = payload["total_miles"]
    else:
        if load.loaded_miles is not None and load.deadhead_miles is not None:
            load.total_miles = float(load.loaded_miles) + float(load.deadhead_miles)

    db.commit()
    db.refresh(load)
    return load
