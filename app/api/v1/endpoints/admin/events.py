from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import (
    EventManager,
    EventReader,
    get_current_admin_user,
    get_current_superadmin,
    get_event_service,
)
from app.db.models import AdminUser
from app.exceptions.schemas import ErrorResponse
from app.schemas.event import (
    EventCreate,
    EventListResponse,
    EventLocationCreate,
    EventLocationListResponse,
    EventLocationResponse,
    EventLocationUpdate,
    EventResponse,
    EventTypeCreate,
    EventTypeResponse,
    EventTypeUpdate,
    EventUpdate,
)
from app.services.event import EventService

router = APIRouter(tags=["events"])


@router.get(
    "/event-types",
    response_model=list[EventTypeResponse],
    status_code=status.HTTP_200_OK,
    summary="Список типов событий",
)
async def list_event_types(
    _current_user: AdminUser = Depends(get_current_admin_user),
    service: EventService = Depends(get_event_service),
) -> list[EventTypeResponse]:
    types = await service.list_event_types()
    return [EventTypeResponse.model_validate(t) for t in types]


@router.post(
    "/event-types",
    response_model=EventTypeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тип события",
    responses={
        403: {"model": ErrorResponse, "description": "Permission denied"},
        409: {"model": ErrorResponse, "description": "Event type already exists"},
    },
)
async def create_event_type(
    data: EventTypeCreate,
    current_user: AdminUser = Depends(get_current_superadmin),
    service: EventService = Depends(get_event_service),
) -> EventTypeResponse:
    event_type = await service.create_event_type(data, current_user)
    return EventTypeResponse.model_validate(event_type)


@router.get(
    "/event-types/{type_id}",
    response_model=EventTypeResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить тип события",
    responses={
        404: {"model": ErrorResponse, "description": "Event type not found"},
    },
)
async def get_event_type(
    type_id: int,
    _current_user: AdminUser = Depends(get_current_admin_user),
    service: EventService = Depends(get_event_service),
) -> EventTypeResponse:
    event_type = await service.get_event_type(type_id)
    return EventTypeResponse.model_validate(event_type)


@router.patch(
    "/event-types/{type_id}",
    response_model=EventTypeResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить тип события",
    responses={
        403: {"model": ErrorResponse, "description": "Permission denied"},
        404: {"model": ErrorResponse, "description": "Event type not found"},
        409: {"model": ErrorResponse, "description": "Event type already exists"},
    },
)
async def update_event_type(
    type_id: int,
    data: EventTypeUpdate,
    current_user: AdminUser = Depends(get_current_superadmin),
    service: EventService = Depends(get_event_service),
) -> EventTypeResponse:
    event_type = await service.update_event_type(type_id, data, current_user)
    return EventTypeResponse.model_validate(event_type)


@router.delete(
    "/event-types/{type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тип события",
    responses={
        403: {"model": ErrorResponse, "description": "Permission denied"},
        404: {"model": ErrorResponse, "description": "Event type not found"},
        409: {"model": ErrorResponse, "description": "Event type is in use"},
    },
)
async def delete_event_type(
    type_id: int,
    _current_user: AdminUser = Depends(get_current_superadmin),
    service: EventService = Depends(get_event_service),
) -> None:
    await service.delete_event_type(type_id)


@router.post(
    "/museums/{museum_id}/event-locations",
    response_model=EventLocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать площадку музея",
    responses={
        403: {"model": ErrorResponse, "description": "Permission denied"},
    },
)
async def create_event_location(
    museum_id: int,
    data: EventLocationCreate,
    current_user: EventManager,
    service: EventService = Depends(get_event_service),
) -> EventLocationResponse:
    location = await service.create_location(museum_id, data, current_user)
    return EventLocationResponse.model_validate(location)


@router.get(
    "/museums/{museum_id}/event-locations",
    response_model=EventLocationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Список площадок музея",
)
async def list_event_locations(
    museum_id: int,
    current_user: EventReader,
    service: EventService = Depends(get_event_service),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> EventLocationListResponse:
    items, total = await service.list_locations(
        museum_id, offset=offset, limit=limit, actor=current_user
    )
    return EventLocationListResponse(
        items=[EventLocationResponse.model_validate(i) for i in items],
        total=total,
    )


@router.get(
    "/museums/{museum_id}/event-locations/{location_id}",
    response_model=EventLocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить площадку музея",
)
async def get_event_location(
    museum_id: int,
    location_id: int,
    current_user: EventReader,
    service: EventService = Depends(get_event_service),
) -> EventLocationResponse:
    location = await service.get_location(museum_id, location_id, current_user)
    return EventLocationResponse.model_validate(location)


@router.patch(
    "/museums/{museum_id}/event-locations/{location_id}",
    response_model=EventLocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить площадку музея",
)
async def update_event_location(
    museum_id: int,
    location_id: int,
    data: EventLocationUpdate,
    current_user: EventManager,
    service: EventService = Depends(get_event_service),
) -> EventLocationResponse:
    location = await service.update_location(
        museum_id, location_id, data, current_user
    )
    return EventLocationResponse.model_validate(location)


@router.delete(
    "/museums/{museum_id}/event-locations/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить площадку музея",
)
async def delete_event_location(
    museum_id: int,
    location_id: int,
    current_user: EventManager,
    service: EventService = Depends(get_event_service),
) -> None:
    await service.delete_location(museum_id, location_id, current_user)


@router.post(
    "/museums/{museum_id}/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать событие",
    responses={
        403: {"model": ErrorResponse, "description": "Permission denied"},
        404: {"model": ErrorResponse, "description": "Type or location not found"},
    },
)
async def create_event(
    museum_id: int,
    data: EventCreate,
    current_user: EventManager,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    event = await service.create_event(museum_id, data, current_user)
    return EventResponse.model_validate(event)


@router.get(
    "/museums/{museum_id}/events",
    response_model=EventListResponse,
    status_code=status.HTTP_200_OK,
    summary="Список событий музея",
)
async def list_events(
    museum_id: int,
    current_user: EventReader,
    service: EventService = Depends(get_event_service),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> EventListResponse:
    items, total = await service.list_events(
        museum_id, offset=offset, limit=limit, actor=current_user
    )
    return EventListResponse(
        items=[EventResponse.model_validate(i) for i in items],
        total=total,
    )


@router.get(
    "/museums/{museum_id}/events/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить событие",
)
async def get_event(
    museum_id: int,
    event_id: int,
    current_user: EventReader,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    event = await service.get_event(museum_id, event_id, current_user)
    return EventResponse.model_validate(event)


@router.patch(
    "/museums/{museum_id}/events/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить событие",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid status transition"},
    },
)
async def update_event(
    museum_id: int,
    event_id: int,
    data: EventUpdate,
    current_user: EventManager,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    event = await service.update_event(museum_id, event_id, data, current_user)
    return EventResponse.model_validate(event)


@router.delete(
    "/museums/{museum_id}/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить событие",
)
async def delete_event(
    museum_id: int,
    event_id: int,
    current_user: EventManager,
    service: EventService = Depends(get_event_service),
) -> None:
    await service.delete_event(museum_id, event_id, current_user)
