from datetime import datetime

from pydantic import BaseModel, Field

from app.enums.database import EventStatusEnum


class EventTypeCreate(BaseModel):
    name: str = Field(max_length=100)


class EventTypeUpdate(BaseModel):
    name: str = Field(max_length=100)


class EventTypeResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventLocationCreate(BaseModel):
    name: str
    description: str | None = None
    address: str
    city: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_active: bool = True


class EventLocationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_active: bool | None = None


class EventLocationResponse(BaseModel):
    id: int
    museum_id: int | None
    name: str
    description: str | None
    address: str
    city: str | None
    country: str | None
    latitude: float | None
    longitude: float | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventLocationListResponse(BaseModel):
    items: list[EventLocationResponse]
    total: int


class EventCreate(BaseModel):
    title: str = Field(max_length=255)
    description: str
    capacity: int = Field(default=0, ge=0)
    date_start: datetime
    date_end: datetime | None = None
    type_id: int
    location_id: int
    is_recurring: bool = False


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    capacity: int | None = Field(default=None, ge=0)
    date_start: datetime | None = None
    date_end: datetime | None = None
    type_id: int | None = None
    location_id: int | None = None
    status: EventStatusEnum | None = None
    is_recurring: bool | None = None


class EventResponse(BaseModel):
    id: int
    museum_id: int
    title: str
    description: str
    capacity: int
    date_start: datetime
    date_end: datetime | None
    status: EventStatusEnum
    is_recurring: bool
    type_id: int
    location_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    items: list[EventResponse]
    total: int
