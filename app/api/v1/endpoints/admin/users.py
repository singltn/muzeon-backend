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
#р
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