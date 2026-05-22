# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
# from app.core.security import hash_password
# from app.db.models.admin_users import AdminUser
# from app.enums.database import UserRoleEnum
# from app.cruds.admin_user import AdminUser
# from app.schemas.auth import CurrentUserResponse
# from app.schemas.user import UserCreate, UserUpdate
#
#
# class UserService:
#     def __init__(self, session: AsyncSession) -> None:
#         self._repo = AdminUser(session)
#         self._session = session
#
#     def _check_museum_access(self, actor: CurrentUserResponse, museum_id: int) -> None:
#         if actor.role != UserRoleEnum.super_admin and actor.museum_id != museum_id:
#             raise PermissionDeniedError("Access denied to this museum")
#
#     async def create(
#         self, museum_id: int, data: UserCreate, actor: CurrentUserResponse
#     ) -> AdminUser:
#         self._check_museum_access(actor, museum_id)
#
#         if data.role == UserRoleEnum.super_admin:
#             raise PermissionDeniedError("Cannot create super_admin through this endpoint")
#         if (
#             data.role == UserRoleEnum.museum_admin
#             and actor.role != UserRoleEnum.super_admin
#         ):
#             raise PermissionDeniedError("Only super_admin can assign museum_admin role")
#
#         if await self._repo.get_by_email(data.email):
#             raise ConflictError("User with this email already exists")
#
#         user = await self._repo.create(
#             email=str(data.email),
#             password=hash_password(data.password),
#             first_name=data.first_name,
#             last_name=data.last_name,
#             role=data.role,
#             museum_id=museum_id,
#             is_active=True,
#             created_by=actor.id,
#             updated_by=actor.id,
#         )
#         await self._session.commit()
#         return user
#
#     async def list_by_museum(
#         self, museum_id: int, offset: int, limit: int, actor: CurrentUserResponse
#     ) -> tuple[list[AdminUser], int]:
#         self._check_museum_access(actor, museum_id)
#         return await self._repo.get_by_museum(museum_id, offset=offset, limit=limit)
#
#     async def get(
#         self, museum_id: int, user_id: int, actor: CurrentUserResponse
#     ) -> AdminUser:
#         self._check_museum_access(actor, museum_id)
#         user = await self._repo.get_by_id_and_museum(user_id, museum_id)
#         if not user:
#             raise NotFoundError("User not found")
#         return user
#
#     async def update(
#         self,
#         museum_id: int,
#         user_id: int,
#         data: UserUpdate,
#         actor: CurrentUserResponse,
#     ) -> AdminUser:
#         user = await self.get(museum_id, user_id, actor)
#         update_kwargs = {k: v for k, v in data.model_dump(exclude_none=True).items()}
#         update_kwargs["updated_by"] = actor.id
#         user = await self._repo.update(user, **update_kwargs)
#         await self._session.commit()
#         return user
#
#     async def delete(
#         self, museum_id: int, user_id: int, actor: CurrentUserResponse
#     ) -> None:
#         user = await self.get(museum_id, user_id, actor)
#         await self._repo.delete(user)
#         await self._session.commit()
