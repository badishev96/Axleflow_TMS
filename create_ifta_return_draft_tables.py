from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

from app.db.base import Base
import app.models.company
import app.models.draft
import app.models.ifta_return_draft
import app.models.ifta_return_state_line_draft

Base.metadata.create_all(bind=engine)
print("OK: IFTA return draft tables ensured.")
