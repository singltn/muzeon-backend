from fastapi import APIRouter, Depends, status, Query

from app.api.dependencies import get_current_superadmin, get_current_admin_user
from app.api.dependencies import get_museum_service
from app.db.models import AdminUser
from app.exceptions.schemas import ErrorResponse
from app.schemas.museum import MuseumCreate, MuseumResponse, MuseumListResponse, MuseumUpdate
from app.services.museum import MuseumService

router = APIRouter(prefix="/museums", tags=["museums"])

@router.get(
    "",
    response_model=MuseumListResponse,
    status_code=status.HTTP_200_OK,
    summary="Список музеев",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authentication required",
        },
        403: {
            "model": ErrorResponse,
            "description": "Permission denied",
        },
    }
)
async def get_museums(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        current_user: AdminUser = Depends(get_current_superadmin),
        service: MuseumService = Depends(get_museum_service),
):
    items, total = await service.list(offset=offset, limit=limit)

    return MuseumListResponse(
        items=[MuseumResponse.model_validate(i) for i in items],
        total=total,
    )

@router.post(
    "",
    response_model=MuseumResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать музей",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authentication required",
        },
        403: {
            "model": ErrorResponse,
            "description": "Permission denied",
        },
        409: {
            "model": ErrorResponse,
            "description": "Museum already exists",
        },
        422: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
    }
)
async def create_museum(
        payload: MuseumCreate,
        current_user: AdminUser = Depends(get_current_superadmin),
        service: MuseumService = Depends(get_museum_service),
) -> MuseumResponse:
    museum = await service.create(payload, current_user)
    return MuseumResponse.model_validate(museum)

@router.get(
    "/{museum_id}",
    response_model=MuseumResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить музей по id",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authentication required",
        },
        403: {
            "model": ErrorResponse,
            "description": "Permission denied",
        },
        404: {
            "model": ErrorResponse,
            "description": "Museum not found",
        },
    }
)
async def get_museum_by_id(
        museum_id: int,
        current_user: AdminUser = Depends(get_current_superadmin),
        service: MuseumService = Depends(get_museum_service),
) -> MuseumResponse:

    museum = await service.get_by_id(museum_id)
    return MuseumResponse.model_validate(museum)

@router.patch(
    "/{museum_id}",
    response_model=MuseumResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить музей",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authentication required",
        },
        403: {
            "model": ErrorResponse,
            "description": "Permission denied",
        },
        404: {
            "model": ErrorResponse,
            "description": "Museum not found",
        },
    }
)
async def update_museum(
        museum_id: int,
        payload: MuseumUpdate,
        current_user: AdminUser = Depends(get_current_superadmin),
        service: MuseumService = Depends(get_museum_service),
) -> MuseumResponse:

    museum = await service.update(museum_id, payload, current_user)
    return MuseumResponse.model_validate(museum)
