from enum import Enum

class AuditAction(str, Enum):
    admin_login = "admin_login"
    admin_logout = "admin_logout"

    admin_user_create = "admin_user_create"
    admin_user_update = "admin_user_update"
    admin_user_delete = "admin_user_delete"
    admin_user_role_assign = "admin_user_role_assign"

    museum_create = "museum_create"
    museum_update = "museum_update"
