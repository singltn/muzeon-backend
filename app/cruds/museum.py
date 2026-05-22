# from sqlalchemy import select
#
# from app.db.models.museum import Museum
# from app.cruds.base import Base
#
#
# class Museum(Base[Museum]):
#     model = Museum
#
#     async def get_by_inn(self, inn: str) -> Museum | None:
#         result = await self.session.execute(
#             select(Museum).where(Museum.inn == inn)
#         )
#         return result.scalar_one_or_none()
#
#     async def get_by_ogrn(self, ogrn: str) -> Museum | None:
#         result = await self.session.execute(
#             select(Museum).where(Museum.ogrn == ogrn)
#         )
#         return result.scalar_one_or_none()
