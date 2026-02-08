from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE loads ADD COLUMN IF NOT EXISTS truck_id INTEGER;"))

print("OK: loads.truck_id ensured.")
