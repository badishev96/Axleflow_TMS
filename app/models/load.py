from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Load(Base):
    __tablename__ = "loads"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    truck_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # NEW: dispatcher attribution (commission-based settlements use this)
    dispatcher_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    loaded_miles: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    deadhead_miles: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    total_miles: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)

    load_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    broker_company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    broker_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    broker_mc_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    broker_agent_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    broker_agent_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    broker_agent_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    pickup_company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    delivery_company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    pickup_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    rate_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    rate_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    commodity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    weight: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dimensions: Mapped[str | None] = mapped_column(String(255), nullable=True)

    load_notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
