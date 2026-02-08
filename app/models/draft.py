from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Draft(Base):
    __tablename__ = "drafts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Tenant isolation (required)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # Type and status
    draft_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. load, expense, fuel_transaction
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")  # draft, reviewing, submitted, discarded

    # Ownership / audit
    created_by_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    updated_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    submitted_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    discarded_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optional linkage to final entity after submit (later)
    target_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Source metadata (manual/ocr/ai/import)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Version for concurrency
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
