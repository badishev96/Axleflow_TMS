from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SettlementRun(Base):
    __tablename__ = "settlement_runs"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)

    # Person-first
    person_type: Mapped[str] = mapped_column(String(20), nullable=False)   # "driver" (v1)
    person_id: Mapped[int] = mapped_column(Integer, nullable=False)        # users.id for now

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="paid")  # v1: paid at creation

    # Pay model snapshot for the run
    pay_model: Mapped[str] = mapped_column(String(20), nullable=False)     # "cpm" | "commission_gross" | "commission_net"
    rate_value: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)

    # Run totals snapshot
    total_miles: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    total_gross: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    total_net: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    total_pay: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
