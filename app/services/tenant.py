from app.db.models import AdminUser
from app.enums.database import UserRoleEnum
from app.exceptions.http import PermissionDeniedError


def check_museum_access(actor: AdminUser, museum_id: int) -> None:
    if actor.role == UserRoleEnum.super_admin:
        return
    if actor.museum_id != museum_id:
        raise PermissionDeniedError()

