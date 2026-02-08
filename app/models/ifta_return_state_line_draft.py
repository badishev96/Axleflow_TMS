from sqlalchemy import String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IFTAReturnStateLineDraft(Base):
    __tablename__ = "ifta_return_state_line_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)

    ifta_return_draft_id: Mapped[int] = mapped_column(
        ForeignKey("ifta_return_drafts.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    state: Mapped[str] = mapped_column(String(2), nullable=False)
    miles: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    gallons: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=0)

    # optional manual credits by state
    credit: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
