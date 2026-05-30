from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import MuseumManager, get_user_service
from app.exceptions.schemas import ErrorResponse
from app.schemas.user import (
    AdminUserBase,
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserUpdate,
)
from app.services.user import UserService

router = APIRouter(prefix="/museums/{museum_id}/users", tags=["museum-users"])


@router.post(
    "",
    response_model=AdminUserBase,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя музея",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Permission denied"},
        409: {"model": ErrorResponse, "description": "User already exists"},
    },
)
async def create_museum_user(
    museum_id: int,
    data: AdminUserCreate,
    current_user: MuseumManager,
    service: UserService = Depends(get_user_service),
) -> AdminUserBase:
    user = await service.create(museum_id, data, current_user)
    return AdminUserBase.model_validate(user)


@router.get(
    "",
    response_model=AdminUserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Список пользователей музея",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Permission denied"},
    },
)
async def list_museum_users(
    museum_id: int,
    current_user: MuseumManager,
    service: UserService = Depends(get_user_service),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> AdminUserListResponse:
    items, total = await service.list_by_museum(
        museum_id, offset=offset, limit=limit, actor=current_user
    )
    return AdminUserListResponse(
        items=[AdminUserBase.model_validate(u) for u in items],
        total=total,
    )


@router.get(
    "/{user_id}",
    response_model=AdminUserBase,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя музея",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Permission denied"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
async def get_museum_user(
    museum_id: int,
    user_id: int,
    current_user: MuseumManager,
    service: UserService = Depends(get_user_service),
) -> AdminUserBase:
    user = await service.get(museum_id, user_id, current_user)
    return AdminUserBase.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=AdminUserBase,
    status_code=status.HTTP_200_OK,
    summary="Обновить пользователя музея",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Permission denied"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
async def update_museum_user(
    museum_id: int,
    user_id: int,
    data: AdminUserUpdate,
    current_user: MuseumManager,
    service: UserService = Depends(get_user_service),
) -> AdminUserBase:
    user = await service.update(museum_id, user_id, data, current_user)
    return AdminUserBase.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя музея",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Permission denied"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
async def delete_museum_user(
    museum_id: int,
    user_id: int,
    current_user: MuseumManager,
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete(museum_id, user_id, current_user)
