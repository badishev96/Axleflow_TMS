from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.hash import bcrypt

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

from app.auth.session_auth import get_current_user

router = APIRouter()

@router.post("/auth/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        email=payload.email.strip().lower(),
        hashed_password=bcrypt.hash(payload.password),
        role=payload.role.strip().lower(),
        company_id=payload.company_id
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User already exists")
    db.refresh(user)
    return user

@router.post("/auth/login")
def login(payload: dict, request: Request, db: Session = Depends(get_db)):
    if "email" not in payload or "password" not in payload:
        raise HTTPException(status_code=422, detail="email and password required")

    email = str(payload["email"]).strip().lower()
    password = str(payload["password"])

    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    request.session["user_id"] = user.id
    request.session["company_id"] = user.company_id
    request.session["role"] = user.role

    return {"status": "ok", "user_id": user.id, "company_id": user.company_id, "role": user.role}

@router.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"status": "ok"}

@router.get("/auth/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
