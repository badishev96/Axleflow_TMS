from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class InventoryEventDraft(Base):
    __tablename__ = "inventory_event_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)

    draft_id: Mapped[int] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity_delta: Mapped[int | None] = mapped_column(Integer, nullable=True)

    unit_cost: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    event_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  
    # added, moved, consumed, lost, damaged, written_off

    from_location_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_location_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    linked_entity_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  
    linked_entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    event_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
