from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FuelCard(Base):
    __tablename__ = "fuel_cards"
    __table_args__ = (
        UniqueConstraint("company_id", "card_number", name="uq_fuel_cards_company_card_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    card_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # Assignment: exactly one of these should be set at a time
    assigned_to_type: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "driver" or "truck"
    assigned_to_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
