from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

# List of columns to ensure exist on load_drafts
columns = [
    ("load_number", "VARCHAR(100)"),

    ("broker_company_name", "VARCHAR(255)"),
    ("broker_address", "VARCHAR(255)"),
    ("broker_mc_number", "VARCHAR(50)"),
    ("broker_agent_name", "VARCHAR(255)"),
    ("broker_agent_phone", "VARCHAR(50)"),
    ("broker_agent_email", "VARCHAR(255)"),

    ("pickup_company_name", "VARCHAR(255)"),
    ("pickup_address", "VARCHAR(255)"),
    ("pickup_hours", "VARCHAR(255)"),
    ("pickup_contact_name", "VARCHAR(255)"),
    ("pickup_contact_phone", "VARCHAR(50)"),

    ("delivery_company_name", "VARCHAR(255)"),
    ("delivery_address", "VARCHAR(255)"),
    ("delivery_hours", "VARCHAR(255)"),
    ("delivery_contact_name", "VARCHAR(255)"),
    ("delivery_contact_phone", "VARCHAR(50)"),

    ("pickup_datetime", "TIMESTAMPTZ"),
    ("delivery_datetime", "TIMESTAMPTZ"),

    ("rate_amount", "NUMERIC(12,2)"),
    ("rate_type", "VARCHAR(50)"),

    ("commodity", "VARCHAR(255)"),
    ("description", "VARCHAR(1000)"),
    ("weight", "VARCHAR(100)"),
    ("dimensions", "VARCHAR(255)"),

    ("load_notes", "VARCHAR(2000)"),
]

with engine.begin() as conn:
    for name, coltype in columns:
        conn.execute(text(f"ALTER TABLE load_drafts ADD COLUMN IF NOT EXISTS {name} {coltype};"))

print("OK: load_drafts columns ensured.")
