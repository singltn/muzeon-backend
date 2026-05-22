from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import Base
from app.db.mixin import DateMixin


class AdminUserAudit(Base, DateMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("admin_user.id"),
        nullable=False
    )