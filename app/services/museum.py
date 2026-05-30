from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.museum import MuseumCrud
from app.db.models.admin_user import AdminUser
from app.db.models.museum import Museum
from app.enums import SubscriptionPlanEnum
from app.enums.database import MuseumStatusEnum, UserRoleEnum
from app.exceptions.http import PermissionDeniedError
from app.exceptions.museum import MuseumAlreadyExistsError, MuseumNotFoundError
from app.schemas.museum import MuseumCreate, MuseumUpdate
from app.services.tenant import check_museum_access

SUPER_ADMIN_ONLY_FIELDS = frozenset(
    {"status", "subscription_plan", "subscription_end_date"}
)


class MuseumService:
    def __init__(self, session: AsyncSession) -> None:
        self.crud = MuseumCrud(session)

    async def get_by_id(self, museum_id: int) -> Museum:
        museum = await self.crud.get_by_id(museum_id)
        if not museum:
            raise MuseumNotFoundError()
        return museum

    async def get_by_id_for_actor(self, museum_id: int, actor: AdminUser) -> Museum:
        museum = await self.get_by_id(museum_id)
        check_museum_access(actor, museum_id)
        return museum

    async def create(self, payload: MuseumCreate, user: AdminUser) -> Museum:
        existing = await self.crud.get_by_inn(payload.inn)
        if existing:
            raise MuseumAlreadyExistsError()

        museum_data = payload.model_dump(exclude_unset=True)
        return await self.crud.create(
            **museum_data,
            status=MuseumStatusEnum.trial,
            subscription_plan=SubscriptionPlanEnum.free,
            subscription_end_date=datetime.now(UTC),
            created_by=user.id,
            updated_by=user.id,
        )

    async def update(
        self,
        museum_id: int,
        payload: MuseumUpdate,
        actor: AdminUser,
    ) -> Museum:
        museum = await self.get_by_id_for_actor(museum_id, actor)
        update_data = payload.model_dump(exclude_unset=True)

        if actor.role != UserRoleEnum.super_admin:
            for field in SUPER_ADMIN_ONLY_FIELDS:
                update_data.pop(field, None)

        return await self.crud.update(
            museum,
            **update_data,
            updated_by=actor.id,
        )

    async def list(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Museum], int]:
        return await self.crud.get_all(offset=offset, limit=limit)
