from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE loads ADD COLUMN IF NOT EXISTS loaded_miles NUMERIC(14,2);"))
    conn.execute(text("ALTER TABLE loads ADD COLUMN IF NOT EXISTS deadhead_miles NUMERIC(14,2);"))
    conn.execute(text("ALTER TABLE loads ADD COLUMN IF NOT EXISTS total_miles NUMERIC(14,2);"))

print("OK: load miles columns ensured.")
