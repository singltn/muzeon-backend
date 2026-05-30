from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.database import MuseumStatusEnum, UserRoleEnum
from app.cruds.admin_user import AdminUser
from app.cruds.museum import Museum
from app.schemas.museum import MuseumCreate, MuseumUpdate
from app.cruds.museum import MuseumCrud
from app.enums import SubscriptionPlanEnum
from app.exceptions.museum import MuseumAlreadyExistsError, MuseumNotFoundError


class MuseumService:
    def __init__(self, session: AsyncSession) -> None:
        self.crud = MuseumCrud(session)

    async def get_by_id(self, museum_id: int) -> Museum:
        museum = await self.crud.get_by_id(museum_id)

        if not museum:
            raise MuseumNotFoundError()

        return museum

    async def create(self, payload: MuseumCreate, user: AdminUser) -> Museum:
        existing = await self.crud.get_by_inn(payload.inn)
        if existing:
            raise MuseumAlreadyExistsError()

        museum_data = payload.model_dump(exclude_unset=True)

        museum = await self.crud.create(
            **museum_data,
            status=MuseumStatusEnum.inactive,
            subscription_plan=SubscriptionPlanEnum.free,
            subscription_end_date=datetime.now(UTC),
            created_by=user.id,
            updated_by=user.id,
        )

        return museum

    async def update(
            self,
            museum_id: int,
            payload: MuseumUpdate,
            user: AdminUser,
    ) -> Museum:

        museum = await self.get_by_id(museum_id)
        update_data = payload.model_dump(exclude_unset=True)

        museum = await self.crud.update(
            museum,
            **update_data,
            updated_by=user.id,
        )

        return museum

    async def list(
            self,
            offset: int = 0,
            limit: int = 20,
    ) -> tuple[list[Museum], int]:
        return await self.crud.get_all(offset=offset, limit=limit)
