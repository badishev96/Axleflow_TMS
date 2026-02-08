from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Truck(Base):
    __tablename__ = "trucks"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    truck_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # Team driver support
    primary_driver_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    secondary_driver_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Manual-first operational fields
    current_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    eta: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
