from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.dashboard import DashboardCrud
from app.cruds.museum import MuseumCrud
from app.db.models.admin_user import AdminUser
from app.enums.database import EventStatusEnum, MuseumStatusEnum, SubscriptionPlanEnum, UserRoleEnum
from app.exceptions.http import PermissionDeniedError
from app.exceptions.museum import MuseumNotFoundError
from app.schemas.dashboard import (
    EventsSummaryFull,
    EventsSummaryStaff,
    ExpiringMuseumItem,
    MuseumAdminDashboardResponse,
    MuseumCardSummary,
    MuseumStaffDashboardResponse,
    MuseumsSummary,
    ProblemMuseumItem,
    StaffSummary,
    StatusCountItem,
    PlanCountItem,
    SubscriptionsSummary,
    SuperAdminDashboardResponse,
    TopMuseumByEventsItem,
    UpcomingEventItem,
)

SUBSCRIPTION_WARNING_DAYS = 7
EVENT_MANAGER_ROLES = frozenset(
    {UserRoleEnum.super_admin, UserRoleEnum.museum_admin, UserRoleEnum.museum_stuff}
)


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self._crud = DashboardCrud(session)
        self._museum_crud = MuseumCrud(session)

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def _subscription_threshold(self) -> datetime:
        return self._now() + timedelta(days=SUBSCRIPTION_WARNING_DAYS)

    def _is_subscription_expiring_soon(self, end_date: datetime) -> bool:
        return end_date <= self._subscription_threshold()

    def _subscription_warning_message(self, end_date: datetime) -> str | None:
        if not self._is_subscription_expiring_soon(end_date):
            return None
        return (
            f"Подписка заканчивается {end_date.strftime('%d.%m.%Y')}. "
            "Обратитесь к администратору платформы для продления."
        )

    def _build_museum_card(self, museum) -> MuseumCardSummary:
        return MuseumCardSummary(
            id=museum.id,
            name=museum.name,
            status=museum.status,
            subscription_plan=museum.subscription_plan,
            subscription_end_date=museum.subscription_end_date,
            subscription_expiring_soon=self._is_subscription_expiring_soon(
                museum.subscription_end_date
            ),
        )

    def _can_edit_events(self, actor: AdminUser) -> bool:
        return actor.role in EVENT_MANAGER_ROLES

    async def _build_upcoming_events(
        self, museum_id: int, actor: AdminUser
    ) -> list[UpcomingEventItem]:
        today_start = self._now().replace(hour=0, minute=0, second=0, microsecond=0)
        events = await self._crud.get_upcoming_events(museum_id, today_start)
        can_edit = self._can_edit_events(actor)
        return [
            UpcomingEventItem(
                id=event.id,
                title=event.title,
                date_start=event.date_start,
                status=event.status,
                capacity=event.capacity,
                occupied=None,
                can_edit=can_edit,
            )
            for event in events
        ]

    async def _get_museum_for_actor(self, actor: AdminUser):
        if actor.museum_id is None:
            raise PermissionDeniedError()
        museum = await self._museum_crud.get_by_id(actor.museum_id)
        if not museum:
            raise MuseumNotFoundError()
        return museum

    async def get_dashboard(
        self, actor: AdminUser
    ) -> SuperAdminDashboardResponse | MuseumAdminDashboardResponse | MuseumStaffDashboardResponse:
        if actor.role == UserRoleEnum.super_admin:
            return await self._super_admin_dashboard()
        if actor.role == UserRoleEnum.museum_admin:
            return await self._museum_admin_dashboard(actor)
        if actor.role == UserRoleEnum.museum_stuff:
            return await self._museum_staff_dashboard(actor)
        raise PermissionDeniedError()

    async def _super_admin_dashboard(self) -> SuperAdminDashboardResponse:
        threshold = self._subscription_threshold()

        status_rows = await self._crud.count_museums_by_status()
        plan_rows = await self._crud.count_museums_by_plan()
        expiring = await self._crud.get_expiring_museums(threshold)
        problem = await self._crud.get_problem_museums()
        top = await self._crud.get_top_museums_by_events(limit=5)

        all_statuses = list(MuseumStatusEnum)
        status_map = {status: 0 for status in all_statuses}
        for status, count in status_rows:
            status_map[status] = count

        all_plans = list(SubscriptionPlanEnum)
        plan_map = {plan: 0 for plan in all_plans}
        for plan, count in plan_rows:
            plan_map[plan] = count

        return SuperAdminDashboardResponse(
            museums=MuseumsSummary(
                total=sum(status_map.values()),
                by_status=[
                    StatusCountItem(status=status, count=count)
                    for status, count in status_map.items()
                ],
            ),
            subscriptions=SubscriptionsSummary(
                by_plan=[
                    PlanCountItem(plan=plan, count=count)
                    for plan, count in plan_map.items()
                ],
            ),
            expiring_subscriptions=[
                ExpiringMuseumItem(
                    id=m.id,
                    name=m.name,
                    subscription_plan=m.subscription_plan,
                    subscription_end_date=m.subscription_end_date,
                )
                for m in expiring
            ],
            problem_museums=[
                ProblemMuseumItem(id=m.id, name=m.name, status=m.status)
                for m in problem
            ],
            top_museums_by_events=[
                TopMuseumByEventsItem(id=m_id, name=name, events_count=count)
                for m_id, name, count in top
            ],
        )

    async def _museum_admin_dashboard(
        self, actor: AdminUser
    ) -> MuseumAdminDashboardResponse:
        museum = await self._get_museum_for_actor(actor)
        museum_id = museum.id

        admin_count = await self._crud.count_users_by_role(
            museum_id, UserRoleEnum.museum_admin
        )
        staff_count = await self._crud.count_users_by_role(
            museum_id, UserRoleEnum.museum_stuff
        )

        return MuseumAdminDashboardResponse(
            museum=self._build_museum_card(museum),
            staff=StaffSummary(
                museum_admin=admin_count,
                museum_staff=staff_count,
            ),
            events=EventsSummaryFull(
                total=await self._crud.count_events_total(museum_id),
                published=await self._crud.count_events_by_status(
                    museum_id, EventStatusEnum.published
                ),
                draft=await self._crud.count_events_by_status(
                    museum_id, EventStatusEnum.draft
                ),
                canceled=await self._crud.count_events_by_status(
                    museum_id, EventStatusEnum.canceled
                ),
                archived=await self._crud.count_events_by_status(
                    museum_id, EventStatusEnum.archived
                ),
            ),
            active_locations_count=await self._crud.count_active_locations(museum_id),
            upcoming_events=await self._build_upcoming_events(museum_id, actor),
        )

    async def _museum_staff_dashboard(
        self, actor: AdminUser
    ) -> MuseumStaffDashboardResponse:
        museum = await self._get_museum_for_actor(actor)
        museum_id = museum.id

        return MuseumStaffDashboardResponse(
            museum=self._build_museum_card(museum),
            events=EventsSummaryStaff(
                total=await self._crud.count_events_total(museum_id),
                published=await self._crud.count_events_by_status(
                    museum_id, EventStatusEnum.published
                ),
                draft=await self._crud.count_events_by_status(
                    museum_id, EventStatusEnum.draft
                ),
            ),
            upcoming_events=await self._build_upcoming_events(museum_id, actor),
            subscription_warning=self._subscription_warning_message(
                museum.subscription_end_date
            ),
        )
