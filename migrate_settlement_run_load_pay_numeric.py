from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.begin() as conn:
    # If load_pay was created as integer earlier, alter it to numeric.
    conn.execute(text("ALTER TABLE settlement_run_loads ALTER COLUMN load_pay TYPE NUMERIC(14,2) USING load_pay::numeric;"))
    conn.execute(text("ALTER TABLE settlement_run_loads ALTER COLUMN load_pay SET DEFAULT 0;"))

print("OK: settlement_run_loads.load_pay is NUMERIC(14,2).")
