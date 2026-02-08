from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class LoadDraft(Base):
    __tablename__ = "load_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Link to DraftBase
    draft_id: Mapped[int] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    # Load identity
    load_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Broker snapshot (rate con style)
    broker_company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    broker_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    broker_mc_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    broker_agent_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    broker_agent_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    broker_agent_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Pickup (shipper)
    pickup_company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Delivery (receiver)
    delivery_company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Dates
    pickup_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Rate
    rate_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    rate_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Freight details
    commodity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    weight: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dimensions: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Notes
    load_notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
