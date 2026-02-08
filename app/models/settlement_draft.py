from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SettlementDraft(Base):
    __tablename__ = "settlement_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)

    draft_id: Mapped[int] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    load_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    truck_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # NEW: drivers snapshot (filled from truck at review time)
    primary_driver_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    secondary_driver_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    commission_basis: Mapped[str | None] = mapped_column(String(10), nullable=True)  # gross or net
    total_commission_percent: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)

    primary_driver_percent: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    secondary_driver_percent: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)

    commission_base_amount: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    commission_pool_amount: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    primary_driver_amount: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    secondary_driver_amount: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
