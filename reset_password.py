from passlib.hash import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

from app.models.user import User  # uses your existing model

EMAIL = "owner3@axleflow.com"
NEW_PASSWORD = "TestPassword123!"

db = SessionLocal()
user = db.query(User).filter(User.email == EMAIL).first()
if not user:
    print("ERROR: user not found:", EMAIL)
    raise SystemExit(1)

user.hashed_password = bcrypt.hash(NEW_PASSWORD)
db.commit()
print("OK: password reset for", EMAIL)
