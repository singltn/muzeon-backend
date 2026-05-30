from sqlalchemy import func, select

from app.db.models.museum import Museum
from app.cruds.base import Base


class MuseumCrud(Base):
    model = Museum

    async def get_by_inn(self, inn: str) -> Museum | None:
        result = await self.session.execute(
            select(Museum).where(Museum.inn == inn)
        )
        return result.scalar_one_or_none()
