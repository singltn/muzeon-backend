from fastapi import APIRouter, Depends, status, Response

from app.api.dependencies import get_current_admin_user
from app.exceptions.schemas import ErrorResponse
from app.db.models import AdminUser
from app.schemas.user import AdminUserBase

router = APIRouter(prefix="/admin/users", tags=["Users"])

@router.get(
    "/me",
    response_model=AdminUserBase,
    status_code=status.HTTP_200_OK,
    summary="Получить текущего администратора",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authentication required / Session expired",
        },
        403: {
            "model": ErrorResponse,
            "description": "Account is inactive",
        },
    }
)
async def get_me_admin(
        user: AdminUser = Depends(get_current_admin_user),
) -> AdminUserBase:
    return AdminUserBase.model_validate(user)



# @router.post("", response_model=UserResponse, status_code=201)
# async def create_user(
#     museum_id: int,
#     data: UserCreate,
#     current_user: CurrentUser,
#     service: UserService = Depends(get_user_service),
# ) -> UserResponse:
#     user = await service.create(museum_id, data, current_user)
#     return UserResponse.model_validate(user)
#
#
# @router.get("", response_model=UserListResponse)
# async def list_users(
#     museum_id: int,
#     current_user: CurrentUser,
#     service: UserService = Depends(get_user_service),
#     offset: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
# ) -> UserListResponse:
#     items, total = await service.list_by_museum(museum_id, offset, limit, current_user)
#     return UserListResponse(
#         items=[UserResponse.model_validate(u) for u in items],
#         total=total,
#     )
#
#
# @router.get("/{user_id}", response_model=UserResponse)
# async def get_user(
#     museum_id: int,
#     user_id: int,
#     current_user: CurrentUser,
#     service: UserService = Depends(get_user_service),
# ) -> UserResponse:
#     user = await service.get(museum_id, user_id, current_user)
#     return UserResponse.model_validate(user)
#
#
# @router.patch("/{user_id}", response_model=UserResponse)
# async def update_user(
#     museum_id: int,
#     user_id: int,
#     data: UserUpdate,
#     current_user: CurrentUser,
#     service: UserService = Depends(get_user_service),
# ) -> UserResponse:
#     user = await service.update(museum_id, user_id, data, current_user)
#     return UserResponse.model_validate(user)
#
#
# @router.delete("/{user_id}", status_code=204)
# async def delete_user(
#     museum_id: int,
#     user_id: int,
#     current_user: CurrentUser,
#     service: UserService = Depends(get_user_service),
# ) -> None:
#     await service.delete(museum_id, user_id, current_user)
