from datetime import datetime
from sqlalchemy import DateTime, func, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class UserAuditMixin:
    created_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_user.id"),
        nullable=True,
    )

    updated_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_user.id"),
        nullable=True,
    )
