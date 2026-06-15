from datetime import datetime

from sqlalchemy import func, select

from app.db.models.admin_user import AdminUser
from app.db.models.event import Event, EventLocation
from app.db.models.museum import Museum
from app.enums.database import EventStatusEnum, MuseumStatusEnum, UserRoleEnum
from app.cruds.base import Base


class DashboardCrud(Base):
    model = Museum

    async def count_museums_by_status(self) -> list[tuple[MuseumStatusEnum, int]]:
        result = await self.session.execute(
            select(Museum.status, func.count())
            .select_from(Museum)
            .group_by(Museum.status)
        )
        return [(row[0], row[1]) for row in result.all()]

    async def count_museums_by_plan(self) -> list[tuple]:
        result = await self.session.execute(
            select(Museum.subscription_plan, func.count())
            .select_from(Museum)
            .group_by(Museum.subscription_plan)
        )
        return [(row[0], row[1]) for row in result.all()]

    async def get_expiring_museums(self, threshold: datetime) -> list[Museum]:
        result = await self.session.execute(
            select(Museum)
            .where(Museum.subscription_end_date <= threshold)
            .order_by(Museum.subscription_end_date.asc())
        )
        return list(result.scalars().all())

    async def get_problem_museums(self) -> list[Museum]:
        result = await self.session.execute(
            select(Museum)
            .where(
                Museum.status.in_(
                    [MuseumStatusEnum.blocked, MuseumStatusEnum.inactive]
                )
            )
            .order_by(Museum.name.asc())
        )
        return list(result.scalars().all())

    async def get_top_museums_by_events(self, limit: int = 5) -> list[tuple[int, str, int]]:
        result = await self.session.execute(
            select(
                Museum.id,
                Museum.name,
                func.count(Event.id).label("events_count"),
            )
            .join(Event, Event.museum_id == Museum.id, isouter=True)
            .group_by(Museum.id, Museum.name)
            .order_by(func.count(Event.id).desc(), Museum.name.asc())
            .limit(limit)
        )
        return [(row[0], row[1], row[2]) for row in result.all()]

    async def count_users_by_role(
        self, museum_id: int, role: UserRoleEnum
    ) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(AdminUser)
            .where(AdminUser.museum_id == museum_id, AdminUser.role == role)
        )
        return result.scalar_one()

    async def count_events_by_status(
        self, museum_id: int, status: EventStatusEnum
    ) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.museum_id == museum_id, Event.status == status)
        )
        return result.scalar_one()

    async def count_events_total(self, museum_id: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.museum_id == museum_id)
        )
        return result.scalar_one()

    async def count_active_locations(self, museum_id: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(EventLocation)
            .where(
                EventLocation.museum_id == museum_id,
                EventLocation.is_active.is_(True),
            )
        )
        return result.scalar_one()

    async def get_upcoming_events(
        self, museum_id: int, from_date: datetime, limit: int = 10
    ) -> list[Event]:
        result = await self.session.execute(
            select(Event)
            .where(
                Event.museum_id == museum_id,
                Event.date_start >= from_date,
            )
            .order_by(Event.date_start.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
