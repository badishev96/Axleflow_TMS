from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE settlement_drafts ADD COLUMN IF NOT EXISTS primary_driver_id INTEGER;"))
    conn.execute(text("ALTER TABLE settlement_drafts ADD COLUMN IF NOT EXISTS secondary_driver_id INTEGER;"))

print("OK: settlement_drafts driver_id columns ensured.")
