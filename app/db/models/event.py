from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixin import DateMixin, UserAuditMixin
from app.db.models.base import Base
from app.enums.database import EventStatusEnum


class Event(Base, DateMixin, UserAuditMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    date_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    date_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[EventStatusEnum] = mapped_column(Enum(EventStatusEnum), nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    museum_id: Mapped[int] = mapped_column(ForeignKey("museum.id"), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("event_type.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("event_location.id"), nullable=False)

    museum = relationship("Museum", back_populates="events")
    event_type = relationship("EventType", back_populates="events")
    location = relationship("EventLocation", back_populates="events")


class EventLocation(Base, DateMixin, UserAuditMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    museum_id: Mapped[int | None] = mapped_column(
        ForeignKey("museum.id"), nullable=True
    )

    museum = relationship("Museum", back_populates="locations")
    events = relationship("Event", back_populates="location")


class EventType(Base, DateMixin, UserAuditMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    events = relationship("Event", back_populates="event_type")
