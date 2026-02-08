from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise SystemExit("DATABASE_URL missing in .env")

engine = create_engine(db_url)

# Import models so they register with Base metadata
from app.db.base import Base  # noqa
import app.models.company  # noqa
import app.models.user  # noqa
import app.models.draft  # noqa

Base.metadata.create_all(bind=engine)
print("OK: drafts table ensured.")
