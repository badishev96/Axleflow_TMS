from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class ExpenseDraft(Base):
    __tablename__ = "expense_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Link to DraftBase (1 typed draft per draft_id)
    draft_id: Mapped[int] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    # Core expense fields
    expense_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")

    expense_category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # fuel, toll, lumper, maintenance, etc.

    # Anchor (Phase 2 rule: explicit anchor)
    anchor_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # load, truck, driver, company
    anchor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Vendor info
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Optional supporting doc / notes
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
