from sqlalchemy import func, select

from app.cruds.base import Base
from app.db.models.event import Event, EventLocation, EventType


class EventCrud(Base):
    model = Event

    async def get_by_id_and_museum(
        self, event_id: int, museum_id: int
    ) -> Event | None:
        result = await self.session.execute(
            select(Event).where(
                Event.id == event_id,
                Event.museum_id == museum_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_museum(
        self, museum_id: int, offset: int = 0, limit: int = 20
    ) -> tuple[list[Event], int]:
        filters = Event.museum_id == museum_id
        count_result = await self.session.execute(
            select(func.count()).select_from(Event).where(filters)
        )
        total = count_result.scalar_one()
        result = await self.session.execute(
            select(Event).where(filters).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total


class EventLocationCrud(Base):
    model = EventLocation

    async def get_by_id_and_museum(
        self, location_id: int, museum_id: int
    ) -> EventLocation | None:
        result = await self.session.execute(
            select(EventLocation).where(
                EventLocation.id == location_id,
                EventLocation.museum_id == museum_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_museum(
        self, museum_id: int, offset: int = 0, limit: int = 20
    ) -> tuple[list[EventLocation], int]:
        filters = EventLocation.museum_id == museum_id
        count_result = await self.session.execute(
            select(func.count()).select_from(EventLocation).where(filters)
        )
        total = count_result.scalar_one()
        result = await self.session.execute(
            select(EventLocation).where(filters).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total


class EventTypeCrud(Base):
    model = EventType

    async def get_by_id(self, type_id: int) -> EventType | None:
        result = await self.session.execute(
            select(EventType).where(EventType.id == type_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[EventType]:
        result = await self.session.execute(select(EventType))
        return list(result.scalars().all())
