from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_password, hash_password
from app.cruds.admin_user import AdminUserCrud
from app.cruds.museum import MuseumCrud
from app.db.models.admin_user import AdminUser
from app.enums.database import UserRoleEnum
from app.exceptions.auth import SMTPError
from app.exceptions.http import PermissionDeniedError
from app.exceptions.museum import MuseumNotFoundError
from app.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.schemas.user import AdminUserCreate, AdminUserUpdate
from app.services.mail import mailer
from app.services.tenant import check_museum_access

MUSEUM_USER_MANAGER_ROLES = frozenset(
    {UserRoleEnum.super_admin, UserRoleEnum.museum_admin}
)

MUSEUM_STAFF_ROLES = frozenset(
    {UserRoleEnum.museum_admin, UserRoleEnum.museum_stuff}
)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._crud = AdminUserCrud(session)
        self._museum_crud = MuseumCrud(session)
        self._session = session

    def _check_can_manage_users(self, actor: AdminUser, museum_id: int) -> None:
        check_museum_access(actor, museum_id)
        if actor.role not in MUSEUM_USER_MANAGER_ROLES:
            raise PermissionDeniedError()

    def _validate_role_assignment(
        self, actor: AdminUser, role: UserRoleEnum
    ) -> None:
        if role == UserRoleEnum.super_admin:
            raise PermissionDeniedError()
        if role == UserRoleEnum.museum_admin and actor.role != UserRoleEnum.super_admin:
            raise PermissionDeniedError()
        if actor.role == UserRoleEnum.museum_admin and role not in MUSEUM_STAFF_ROLES - {
            UserRoleEnum.museum_admin
        }:
            raise PermissionDeniedError()

    async def create(
        self, museum_id: int, data: AdminUserCreate, actor: AdminUser
    ) -> AdminUser:
        self._check_can_manage_users(actor, museum_id)
        self._validate_role_assignment(actor, data.role)

        if await self._crud.get_by_email(str(data.email)):
            raise UserAlreadyExistsError()

        museum = await self._museum_crud.get_by_id(museum_id)
        if not museum:
            raise MuseumNotFoundError()

        plain_password = generate_password()
        user = await self._crud.create(
            email=str(data.email),
            password=hash_password(plain_password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
            museum_id=museum_id,
            is_active=True,
            created_by=actor.id,
            updated_by=actor.id,
        )

        try:
            await mailer.send_credentials_email(
                to_email=str(data.email),
                password=plain_password,
                museum_name=museum.name,
            )
        except SMTPError:
            await self._crud.delete(user)
            raise

        loaded = await self._crud.get_by_id_and_museum(user.id, museum_id)
        return loaded or user

    async def list_by_museum(
        self, museum_id: int, offset: int, limit: int, actor: AdminUser
    ) -> tuple[list[AdminUser], int]:
        self._check_can_manage_users(actor, museum_id)
        return await self._crud.get_by_museum(museum_id, offset=offset, limit=limit)

    async def get(
        self, museum_id: int, user_id: int, actor: AdminUser
    ) -> AdminUser:
        self._check_can_manage_users(actor, museum_id)
        user = await self._crud.get_by_id_and_museum(user_id, museum_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def update(
        self,
        museum_id: int,
        user_id: int,
        data: AdminUserUpdate,
        actor: AdminUser,
    ) -> AdminUser:
        user = await self.get(museum_id, user_id, actor)
        update_kwargs = data.model_dump(exclude_none=True)

        if "role" in update_kwargs:
            self._validate_role_assignment(actor, update_kwargs["role"])

        if user.id == actor.id and update_kwargs.get("is_active") is False:
            raise PermissionDeniedError()

        update_kwargs["updated_by"] = actor.id
        updated = await self._crud.update(user, **update_kwargs)
        loaded = await self._crud.get_by_id_and_museum(updated.id, museum_id)
        return loaded or updated

    async def delete(
        self, museum_id: int, user_id: int, actor: AdminUser
    ) -> None:
        user = await self.get(museum_id, user_id, actor)
        if user.id == actor.id:
            raise PermissionDeniedError()
        await self._crud.delete(user)
