from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

from app.db.base import Base
import app.models.company
import app.models.draft
import app.models.inventory_event_draft
import app.models.inventory_event

Base.metadata.create_all(bind=engine)
print("OK: inventory_event_drafts + inventory_events tables ensured.")
