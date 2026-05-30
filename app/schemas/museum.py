from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.enums.database import MuseumStatusEnum, SubscriptionPlanEnum


class MuseumCreate(BaseModel):
    name: str
    legal_name: str
    inn: str = Field(min_length=10, max_length=12)
    ogrn: str = Field(min_length=13, max_length=13)
    email: EmailStr
    phone: str = Field(min_length=11, max_length=12)
    address: str


class MuseumUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    status: MuseumStatusEnum | None = None
    subscription_plan: SubscriptionPlanEnum | None = None
    subscription_end_date: datetime | None = None


class MuseumBrief(BaseModel):
    id: int
    name: str
    status: MuseumStatusEnum

    model_config = {"from_attributes": True}


class MuseumResponse(BaseModel):
    id: int
    name: str
    legal_name: str
    inn: str
    ogrn: str
    email: str
    phone: str
    address: str
    status: MuseumStatusEnum
    subscription_plan: SubscriptionPlanEnum
    subscription_end_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MuseumListResponse(BaseModel):
    items: list[MuseumResponse]
    total: int
