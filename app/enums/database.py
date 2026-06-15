from enum import Enum

class MuseumStatusEnum(str, Enum):
    active = "active"
    trial = "trial"
    inactive = "inactive"
    blocked = "blocked"


class SubscriptionPlanEnum(str, Enum):
    free = "free"
    basic = "basic"
    premium = "premium"


class UserRoleEnum(str, Enum):
    super_admin = "super_admin"
    museum_admin = "museum_admin"
    museum_stuff = "museum_stuff"


class EventStatusEnum(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"
    canceled = "canceled"