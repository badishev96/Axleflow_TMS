from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

from app.db.base import Base
import app.models.company
import app.models.settlement_run
import app.models.settlement_run_load

Base.metadata.create_all(bind=engine)
print("OK: settlement_runs and settlement_run_loads tables ensured.")
