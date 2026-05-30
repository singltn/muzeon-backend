from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.event import EventCrud, EventLocationCrud, EventTypeCrud
from app.db.models import AdminUser
from app.db.models.event import Event, EventLocation
from app.enums.database import EventStatusEnum
from app.exceptions.event import (
    EventLocationNotFoundError,
    EventNotFoundError,
    EventTypeNotFoundError,
    InvalidEventStatusTransitionError,
)
from app.schemas.event import (
    EventCreate,
    EventLocationCreate,
    EventLocationUpdate,
    EventUpdate,
)
from app.services.tenant import check_museum_access

ALLOWED_STATUS_TRANSITIONS: dict[EventStatusEnum, set[EventStatusEnum]] = {
    EventStatusEnum.draft: {
        EventStatusEnum.published,
        EventStatusEnum.canceled,
    },
    EventStatusEnum.published: {
        EventStatusEnum.archived,
        EventStatusEnum.canceled,
    },
    EventStatusEnum.archived: set(),
    EventStatusEnum.canceled: set(),
}


class EventService:
    def __init__(self, session: AsyncSession) -> None:
        self._events = EventCrud(session)
        self._locations = EventLocationCrud(session)
        self._types = EventTypeCrud(session)

    async def _ensure_event_type(self, type_id: int) -> None:
        if not await self._types.get_by_id(type_id):
            raise EventTypeNotFoundError()

    async def _ensure_location_in_museum(
        self, location_id: int, museum_id: int
    ) -> EventLocation:
        location = await self._locations.get_by_id_and_museum(location_id, museum_id)
        if not location:
            raise EventLocationNotFoundError()
        return location

    def _validate_status_transition(
        self, current: EventStatusEnum, new: EventStatusEnum
    ) -> None:
        if current == new:
            return
        allowed = ALLOWED_STATUS_TRANSITIONS.get(current, set())
        if new not in allowed:
            raise InvalidEventStatusTransitionError()

    async def list_event_types(self) -> list:
        return await self._types.list_all()

    async def create_location(
        self,
        museum_id: int,
        data: EventLocationCreate,
        actor: AdminUser,
    ) -> EventLocation:
        check_museum_access(actor, museum_id)
        return await self._locations.create(
            **data.model_dump(),
            museum_id=museum_id,
            created_by=actor.id,
            updated_by=actor.id,
        )

    async def list_locations(
        self,
        museum_id: int,
        offset: int,
        limit: int,
        actor: AdminUser,
    ) -> tuple[list[EventLocation], int]:
        check_museum_access(actor, museum_id)
        return await self._locations.get_by_museum(museum_id, offset=offset, limit=limit)

    async def get_location(
        self, museum_id: int, location_id: int, actor: AdminUser
    ) -> EventLocation:
        check_museum_access(actor, museum_id)
        location = await self._locations.get_by_id_and_museum(location_id, museum_id)
        if not location:
            raise EventLocationNotFoundError()
        return location

    async def update_location(
        self,
        museum_id: int,
        location_id: int,
        data: EventLocationUpdate,
        actor: AdminUser,
    ) -> EventLocation:
        location = await self.get_location(museum_id, location_id, actor)
        return await self._locations.update(
            location,
            **data.model_dump(exclude_none=True),
            updated_by=actor.id,
        )

    async def delete_location(
        self, museum_id: int, location_id: int, actor: AdminUser
    ) -> None:
        location = await self.get_location(museum_id, location_id, actor)
        await self._locations.delete(location)

    async def create_event(
        self,
        museum_id: int,
        data: EventCreate,
        actor: AdminUser,
    ) -> Event:
        check_museum_access(actor, museum_id)
        await self._ensure_event_type(data.type_id)
        await self._ensure_location_in_museum(data.location_id, museum_id)

        return await self._events.create(
            **data.model_dump(),
            museum_id=museum_id,
            status=EventStatusEnum.draft,
            created_by=actor.id,
            updated_by=actor.id,
        )

    async def list_events(
        self,
        museum_id: int,
        offset: int,
        limit: int,
        actor: AdminUser,
    ) -> tuple[list[Event], int]:
        check_museum_access(actor, museum_id)
        return await self._events.get_by_museum(museum_id, offset=offset, limit=limit)

    async def get_event(
        self, museum_id: int, event_id: int, actor: AdminUser
    ) -> Event:
        check_museum_access(actor, museum_id)
        event = await self._events.get_by_id_and_museum(event_id, museum_id)
        if not event:
            raise EventNotFoundError()
        return event

    async def update_event(
        self,
        museum_id: int,
        event_id: int,
        data: EventUpdate,
        actor: AdminUser,
    ) -> Event:
        event = await self.get_event(museum_id, event_id, actor)
        update_data = data.model_dump(exclude_none=True)

        if "status" in update_data:
            self._validate_status_transition(event.status, update_data["status"])

        if "type_id" in update_data:
            await self._ensure_event_type(update_data["type_id"])

        if "location_id" in update_data:
            await self._ensure_location_in_museum(update_data["location_id"], museum_id)

        return await self._events.update(
            event,
            **update_data,
            updated_by=actor.id,
        )

    async def delete_event(
        self, museum_id: int, event_id: int, actor: AdminUser
    ) -> None:
        event = await self.get_event(museum_id, event_id, actor)
        await self._events.delete(event)
