from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    load_id: Mapped[int] = mapped_column(Integer, nullable=False)
    truck_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # NEW: driver attribution
    primary_driver_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    secondary_driver_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    commission_basis: Mapped[str] = mapped_column(String(10), nullable=False)
    total_commission_percent: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)

    primary_driver_percent: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    secondary_driver_percent: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False, default=0)

    commission_base_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    commission_pool_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    primary_driver_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    secondary_driver_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
