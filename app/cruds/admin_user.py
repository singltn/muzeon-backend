from sqlalchemy import func, select

from app.db.models.admin_user import AdminUser
from app.cruds.base import Base


class AdminUserCrud(Base):
    model = AdminUser

    async def get_by_email(self, email: str) -> AdminUser | None:
        result = await self.session.execute(
            select(AdminUser).where(AdminUser.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_museum(
        self, user_id: int, museum_id: int
    ) -> AdminUser | None:
        result = await self.session.execute(
            select(AdminUser).where(
                AdminUser.id == user_id,
                AdminUser.museum_id == museum_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_museum(
        self, museum_id: int, offset: int = 0, limit: int = 20
    ) -> tuple[list[AdminUser], int]:
        filters = AdminUser.museum_id == museum_id
        count_result = await self.session.execute(
            select(func.count()).select_from(AdminUser).where(filters)
        )
        total = count_result.scalar_one()
        result = await self.session.execute(
            select(AdminUser).where(filters).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total
