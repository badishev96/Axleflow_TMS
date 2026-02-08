from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=72)
    role: str = "owner"
    company_id: int

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    company_id: int

# Backward-compatible alias for existing auth.py imports
class UserRead(UserOut):
    pass
