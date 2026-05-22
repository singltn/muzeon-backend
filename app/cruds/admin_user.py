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
