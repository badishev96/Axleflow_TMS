from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FuelTransaction(Base):
    __tablename__ = "fuel_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    fuel_card_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    transaction_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)

    gallons: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    assignment_context_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    assignment_context_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
