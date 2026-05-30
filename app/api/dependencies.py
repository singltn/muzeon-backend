from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis
from app.db.session import get_db
from app.services.auth import AuthService
from app.services.museum import MuseumService
from app.services.user import UserService
from app.services.event import EventService
from app.core.config import settings
from app.db.models import AdminUser
from app.exceptions.auth import AuthenticationRequiredError
from app.exceptions.http import PermissionDeniedError
from app.services.session import SessionService
from app.enums import UserRoleEnum

def get_auth_service(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(session, redis)

def get_session_service(
    redis: Redis = Depends(get_redis),
) -> SessionService:
    return SessionService(redis)

def get_museum_service(session: AsyncSession = Depends(get_db)) -> MuseumService:
    return MuseumService(session)

def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


def get_event_service(session: AsyncSession = Depends(get_db)) -> EventService:
    return EventService(session)

async def get_current_admin_user(
    request: Request,
    service: AuthService = Depends(get_auth_service),

) -> AdminUser:
    session_id = request.cookies.get(settings.SESSION_COOKIE)
    if not session_id:
        raise AuthenticationRequiredError
    return await service.get_current_admin_user(session_id)

async def get_current_superadmin(
    current_user: AdminUser = Depends(get_current_admin_user),
) -> AdminUser:
    if current_user.role != UserRoleEnum.super_admin:
        raise PermissionDeniedError

    return current_user


def require_roles(*roles: UserRoleEnum) -> Callable:
    async def _check(
        current_user: AdminUser = Depends(get_current_admin_user),
    ) -> AdminUser:
        if current_user.role not in roles:
            raise PermissionDeniedError()
        return current_user

    return _check


MuseumManager = Annotated[
    AdminUser,
    Depends(require_roles(UserRoleEnum.super_admin, UserRoleEnum.museum_admin)),
]

EventManager = Annotated[
    AdminUser,
    Depends(
        require_roles(
            UserRoleEnum.super_admin,
            UserRoleEnum.museum_admin,
            UserRoleEnum.content,
        )
    ),
]

EventReader = Annotated[
    AdminUser,
    Depends(
        require_roles(
            UserRoleEnum.super_admin,
            UserRoleEnum.museum_admin,
            UserRoleEnum.content,
            UserRoleEnum.marketer,
            UserRoleEnum.analyst,
        )
    ),
]