from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class InventoryLocation(Base):
    __tablename__ = "inventory_locations"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    location_type: Mapped[str] = mapped_column(String(20), nullable=False)  # truck, trailer, yard, attachment
    location_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # optional link to asset id
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # human readable label

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
