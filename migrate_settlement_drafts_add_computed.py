from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

cols = [
    ("commission_base_amount", "NUMERIC(14,2)"),
    ("commission_pool_amount", "NUMERIC(14,2)"),
    ("primary_driver_amount", "NUMERIC(14,2)"),
    ("secondary_driver_amount", "NUMERIC(14,2)"),
]

with engine.begin() as conn:
    for name, coltype in cols:
        conn.execute(text(f"ALTER TABLE settlement_drafts ADD COLUMN IF NOT EXISTS {name} {coltype};"))

print("OK: settlement_drafts computed columns ensured.")
