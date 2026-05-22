from datetime import datetime
from sqlalchemy import BigInteger, String, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base
from app.enums.database import MuseumStatusEnum, SubscriptionPlanEnum
from app.db.mixin import DateMixin, UserAuditMixin


class Museum(Base, DateMixin, UserAuditMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    ogrn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(11), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[MuseumStatusEnum] = mapped_column(Enum(MuseumStatusEnum), nullable=False)
    subscription_plan: Mapped[SubscriptionPlanEnum] = mapped_column(Enum(SubscriptionPlanEnum), nullable=False)
    subscription_end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    admins = relationship(
        "AdminUser",
        back_populates="museum",
        foreign_keys="AdminUser.museum_id"
    )

    events = relationship(
        "Event",
        back_populates="museum",
        foreign_keys="Event.museum_id"
    )

    locations = relationship(
        "EventLocation",
        back_populates="museum",
        foreign_keys="EventLocation.museum_id"
    )