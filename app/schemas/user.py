from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.enums.database import UserRoleEnum
from app.schemas.museum import MuseumBrief


class AdminUserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRoleEnum = UserRoleEnum.museum_stuff


class AdminUserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    role: UserRoleEnum | None = None
    is_active: bool | None = None

class AdminUserShallow(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRoleEnum
    is_active: bool

    model_config = {"from_attributes": True}

class AdminUserBase(AdminUserShallow):
    museum: MuseumBrief | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    items: list[AdminUserBase]
    total: int
