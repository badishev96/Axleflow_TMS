from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class IFTAReturnDraft(Base):
    __tablename__ = "ifta_return_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)

    draft_id: Mapped[int] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    quarter: Mapped[str | None] = mapped_column(String(10), nullable=True)  # e.g. 2026Q1
    status_note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Totals (optional computed later, store for simplicity)
    total_miles: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    total_gallons: Mapped[float | None] = mapped_column(Numeric(14, 3), nullable=True)
    mpg: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)

    total_tax_due: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    total_credits: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    net_due: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
