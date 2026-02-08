from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InventoryEvent(Base):
    __tablename__ = "inventory_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_delta: Mapped[int] = mapped_column(Integer, nullable=False)

    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    event_type: Mapped[str] = mapped_column(String(20), nullable=False)

    from_location_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_location_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    linked_entity_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    linked_entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
