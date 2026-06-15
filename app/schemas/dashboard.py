from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel

from app.enums.database import EventStatusEnum, MuseumStatusEnum, SubscriptionPlanEnum


class StatusCountItem(BaseModel):
    status: MuseumStatusEnum
    count: int


class PlanCountItem(BaseModel):
    plan: SubscriptionPlanEnum
    count: int


class MuseumsSummary(BaseModel):
    total: int
    by_status: list[StatusCountItem]


class SubscriptionsSummary(BaseModel):
    by_plan: list[PlanCountItem]


class ExpiringMuseumItem(BaseModel):
    id: int
    name: str
    subscription_plan: SubscriptionPlanEnum
    subscription_end_date: datetime


class ProblemMuseumItem(BaseModel):
    id: int
    name: str
    status: MuseumStatusEnum


class TopMuseumByEventsItem(BaseModel):
    id: int
    name: str
    events_count: int


class SuperAdminDashboardResponse(BaseModel):
    role: Literal["super_admin"] = "super_admin"
    museums: MuseumsSummary
    subscriptions: SubscriptionsSummary
    expiring_subscriptions: list[ExpiringMuseumItem]
    problem_museums: list[ProblemMuseumItem]
    top_museums_by_events: list[TopMuseumByEventsItem]


class MuseumCardSummary(BaseModel):
    id: int
    name: str
    status: MuseumStatusEnum
    subscription_plan: SubscriptionPlanEnum
    subscription_end_date: datetime
    subscription_expiring_soon: bool


class StaffSummary(BaseModel):
    museum_admin: int
    museum_staff: int


class EventsSummaryFull(BaseModel):
    total: int
    published: int
    draft: int
    canceled: int
    archived: int


class EventsSummaryStaff(BaseModel):
    total: int
    published: int
    draft: int


class UpcomingEventItem(BaseModel):
    id: int
    title: str
    date_start: datetime
    status: EventStatusEnum
    capacity: int
    occupied: int | None = None
    can_edit: bool


class MuseumAdminDashboardResponse(BaseModel):
    role: Literal["museum_admin"] = "museum_admin"
    museum: MuseumCardSummary
    staff: StaffSummary
    events: EventsSummaryFull
    active_locations_count: int
    upcoming_events: list[UpcomingEventItem]


class MuseumStaffDashboardResponse(BaseModel):
    role: Literal["museum_stuff"] = "museum_stuff"
    museum: MuseumCardSummary
    events: EventsSummaryStaff
    upcoming_events: list[UpcomingEventItem]
    subscription_warning: str | None = None


DashboardResponse = Union[
    SuperAdminDashboardResponse,
    MuseumAdminDashboardResponse,
    MuseumStaffDashboardResponse,
]
