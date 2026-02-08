from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

from app.db.base import Base  # noqa
import app.models.company  # noqa
import app.models.user  # noqa
import app.models.draft  # noqa
import app.models.load_draft  # noqa

Base.metadata.create_all(bind=engine)
print("OK: load_drafts table ensured.")
