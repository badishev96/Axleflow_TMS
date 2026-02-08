from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

from app.db.base import Base
import app.models.company
import app.models.user
import app.models.draft
import app.models.expense_draft

Base.metadata.create_all(bind=engine)
print("OK: expense_drafts table ensured.")
