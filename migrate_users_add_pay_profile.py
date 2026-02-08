from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pay_model VARCHAR(30);"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pay_rate NUMERIC(14,4);"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pay_commission_basis VARCHAR(10);"))  # gross/net (only for commission)
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pay_effective_date DATE;"))

print("OK: user pay profile columns ensured.")
