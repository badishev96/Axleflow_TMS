from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    company = relationship("Company")

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Role
    role: Mapped[str] = mapped_column(String(50), default="owner", nullable=False)

    # Pay Profile (for drivers/dispatchers; safe to be NULL for others)
    pay_model: Mapped[str | None] = mapped_column(String(30), nullable=True)                 # cpm | commission_gross | commission_net | flat
    pay_rate: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)           # 0.70, 30.0000 etc
    pay_commission_basis: Mapped[str | None] = mapped_column(String(10), nullable=True)     # gross/net (optional)
    pay_effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
