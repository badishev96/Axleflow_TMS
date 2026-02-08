from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class FuelTransactionDraft(Base):
    __tablename__ = "fuel_transaction_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Link to DraftBase (1 typed draft per draft_id)
    draft_id: Mapped[int] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    fuel_card_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    transaction_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)

    gallons: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    total_cost: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Context (manual for now)
    assignment_context_type: Mapped[str | None] = mapped_column(String(10), nullable=True)  # driver or truck
    assignment_context_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
