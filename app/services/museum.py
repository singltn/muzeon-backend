# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
# from app.core.security import hash_password
# from app.db.models.museum import Museum
# from app.enums.database import MuseumStatusEnum, UserRoleEnum
# from app.cruds.admin_user import AdminUser
# from app.cruds.museum import Museum
# from app.schemas.auth import CurrentUserResponse
# from app.schemas.museum import MuseumCreate, MuseumUpdate
#
#
# class MuseumService:
#     def __init__(self, session: AsyncSession) -> None:
#         self._museum_repo = Museum(session)
#         self._user_repo = AdminUser(session)
#         self._session = session
#
#     async def create(self, data: MuseumCreate, actor: CurrentUserResponse) -> Museum:
#         if await self._museum_repo.get_by_inn(data.inn):
#             raise ConflictError("Museum with this INN already exists")
#         if await self._museum_repo.get_by_ogrn(data.ogrn):
#             raise ConflictError("Museum with this OGRN already exists")
#         if await self._user_repo.get_by_email(data.admin_email):
#             raise ConflictError("User with this email already exists")
#
#         museum = await self._museum_repo.create(
#             name=data.name,
#             legal_name=data.legal_name,
#             inn=data.inn,
#             ogrn=data.ogrn,
#             email=str(data.email),
#             phone=data.phone,
#             address=data.address,
#             status=MuseumStatusEnum.trial,
#             subscription_plan=data.subscription_plan,
#             subscription_end_date=data.subscription_end_date,
#             created_by=actor.id,
#             updated_by=actor.id,
#         )
#         await self._user_repo.create(
#             email=str(data.admin_email),
#             password=hash_password(data.admin_password),
#             first_name=data.admin_first_name,
#             last_name=data.admin_last_name,
#             role=UserRoleEnum.museum_admin,
#             museum_id=museum.id,
#             is_active=True,
#             created_by=actor.id,
#             updated_by=actor.id,
#         )
#         await self._session.commit()
#         return museum
#
#     async def get(self, museum_id: int, actor: CurrentUserResponse) -> Museum:
#         museum = await self._museum_repo.get_by_id(museum_id)
#         if not museum:
#             raise NotFoundError("Museum not found")
#         if actor.role != UserRoleEnum.super_admin and actor.museum_id != museum_id:
#             raise NotFoundError("Museum not found")
#         return museum
#
#     async def list_all(
#         self, offset: int = 0, limit: int = 20
#     ) -> tuple[list[Museum], int]:
#         return await self._museum_repo.get_all(offset=offset, limit=limit)
#
#     async def update(
#         self, museum_id: int, data: MuseumUpdate, actor: CurrentUserResponse
#     ) -> Museum:
#         museum = await self.get(museum_id, actor)
#
#         if actor.role != UserRoleEnum.super_admin:
#             if (
#                 data.status is not None
#                 or data.subscription_plan is not None
#                 or data.subscription_end_date is not None
#             ):
#                 raise PermissionDeniedError(
#                     "Only super_admin can change status or subscription"
#                 )
#
#         update_kwargs = {k: v for k, v in data.model_dump(exclude_none=True).items()}
#         update_kwargs["updated_by"] = actor.id
#         museum = await self._museum_repo.update(museum, **update_kwargs)
#         await self._session.commit()
#         return museum
#
#     async def delete(self, museum_id: int) -> None:
#         museum = await self._museum_repo.get_by_id(museum_id)
#         if not museum:
#             raise NotFoundError("Museum not found")
#         await self._museum_repo.delete(museum)
#         await self._session.commit()
