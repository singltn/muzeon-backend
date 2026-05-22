from sqlalchemy import BigInteger, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from app.db.models.base import Base
from app.db.mixin import DateMixin, UserAuditMixin
from app.enums.database import UserRoleEnum


class AdminUser(Base, DateMixin, UserAuditMixin):

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(length=100),unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    museum_id: Mapped[int | None] = mapped_column(ForeignKey("museum.id"), nullable=True)

    museum = relationship(
        "Museum",
        back_populates="admins",
        foreign_keys=[museum_id]
    )