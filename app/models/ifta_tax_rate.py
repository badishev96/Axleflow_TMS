from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IFTATaxRate(Base):
    __tablename__ = "ifta_tax_rates"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    state: Mapped[str] = mapped_column(String(2), nullable=False)
    quarter: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g. 2026Q1

    tax_rate_per_gallon: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
