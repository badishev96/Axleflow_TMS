from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SettlementRunLoad(Base):
    __tablename__ = "settlement_run_loads"
    __table_args__ = (
        UniqueConstraint("company_id", "person_type", "person_id", "load_id", name="uq_runload_person_load"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    settlement_run_id: Mapped[int] = mapped_column(ForeignKey("settlement_runs.id", ondelete="CASCADE"), index=True, nullable=False)

    person_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "driver"
    person_id: Mapped[int] = mapped_column(Integer, nullable=False)

    load_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # per-load pay snapshot (money)
    load_pay: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
