# from datetime import datetime, timezone
# from unittest.mock import AsyncMock, MagicMock
#
# import pytest
# from httpx import AsyncClient
#
# from app.api.dependencies import get_current_user
# from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
# from app.enums.database import MuseumStatusEnum, SubscriptionPlanEnum, UserRoleEnum
# from app.main import app
# from app.schemas.auth import CurrentUserResponse
#
# MUSEUM_PAYLOAD = {
#     "name": "Эрмитаж",
#     "legal_name": "ФГБУК «Государственный Эрмитаж»",
#     "inn": "7813030002",
#     "ogrn": "1027809238334",
#     "email": "info@hermitage.ru",
#     "phone": "78123118900",
#     "address": "Дворцовая набережная, 34",
#     "subscription_plan": "free",
#     "subscription_end_date": "2027-01-01T00:00:00Z",
#     "admin_email": "admin@hermitage.ru",
#     "admin_first_name": "Иван",
#     "admin_last_name": "Иванов",
#     "admin_password": "securepass123",
# }
#
#
# def _make_museum(museum_id: int = 1) -> MagicMock:
#     m = MagicMock()
#     m.id = museum_id
#     m.name = "Эрмитаж"
#     m.legal_name = "ФГБУК «Государственный Эрмитаж»"
#     m.inn = "7813030002"
#     m.ogrn = "1027809238334"
#     m.email = "info@hermitage.ru"
#     m.phone = "78123118900"
#     m.address = "Дворцовая набережная, 34"
#     m.status = MuseumStatusEnum.trial
#     m.subscription_plan = SubscriptionPlanEnum.free
#     m.subscription_end_date = datetime(2027, 1, 1, tzinfo=timezone.utc)
#     m.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
#     m.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
#     return m
#
#
# async def test_create_museum(client: AsyncClient, mock_museum_service):
#     mock_museum_service.create = AsyncMock(return_value=_make_museum())
#     response = await client.post("/api/v1/museums", json=MUSEUM_PAYLOAD)
#     assert response.status_code == 201
#     assert response.json()["inn"] == "7813030002"
#
#
# async def test_create_museum_forbidden_for_museum_admin(
#     client: AsyncClient, mock_museum_service, museum_admin: CurrentUserResponse
# ):
#     app.dependency_overrides[get_current_user] = lambda: museum_admin
#     try:
#         response = await client.post("/api/v1/museums", json=MUSEUM_PAYLOAD)
#         assert response.status_code == 403
#     finally:
#         from app.enums.database import UserRoleEnum
#         super_admin = CurrentUserResponse(
#             id=1, email="admin@muzeon.ru", first_name="Super", last_name="Admin",
#             role=UserRoleEnum.super_admin, museum_id=None,
#         )
#         app.dependency_overrides[get_current_user] = lambda: super_admin
#
#
# async def test_create_museum_duplicate_inn(client: AsyncClient, mock_museum_service):
#     mock_museum_service.create = AsyncMock(
#         side_effect=ConflictError("Museum with this INN already exists")
#     )
#     response = await client.post("/api/v1/museums", json=MUSEUM_PAYLOAD)
#     assert response.status_code == 409
#     assert "INN" in response.json()["detail"]
#
#
# async def test_create_museum_duplicate_admin_email(
#     client: AsyncClient, mock_museum_service
# ):
#     mock_museum_service.create = AsyncMock(
#         side_effect=ConflictError("User with this email already exists")
#     )
#     response = await client.post("/api/v1/museums", json=MUSEUM_PAYLOAD)
#     assert response.status_code == 409
#
#
# async def test_list_museums(client: AsyncClient, mock_museum_service):
#     museums = [_make_museum(i) for i in range(1, 4)]
#     mock_museum_service.list_all = AsyncMock(return_value=(museums, 3))
#
#     response = await client.get("/api/v1/museums")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["total"] == 3
#     assert len(data["items"]) == 3
#
#
# async def test_list_museums_pagination(client: AsyncClient, mock_museum_service):
#     mock_museum_service.list_all = AsyncMock(return_value=([], 0))
#     response = await client.get("/api/v1/museums?offset=0&limit=10")
#     assert response.status_code == 200
#     mock_museum_service.list_all.assert_called_once_with(offset=0, limit=10)
#
#
# async def test_get_museum(client: AsyncClient, mock_museum_service):
#     mock_museum_service.get = AsyncMock(return_value=_make_museum())
#     response = await client.get("/api/v1/museums/1")
#     assert response.status_code == 200
#     assert response.json()["id"] == 1
#
#
# async def test_get_museum_not_found(client: AsyncClient, mock_museum_service):
#     mock_museum_service.get = AsyncMock(
#         side_effect=NotFoundError("Museum not found")
#     )
#     response = await client.get("/api/v1/museums/999")
#     assert response.status_code == 404
#
#
# async def test_update_museum(client: AsyncClient, mock_museum_service):
#     updated = _make_museum()
#     updated.name = "Новое название"
#     mock_museum_service.update = AsyncMock(return_value=updated)
#
#     response = await client.patch("/api/v1/museums/1", json={"name": "Новое название"})
#     assert response.status_code == 200
#
#
# async def test_update_museum_subscription_forbidden(
#     client: AsyncClient, mock_museum_service
# ):
#     mock_museum_service.update = AsyncMock(
#         side_effect=PermissionDeniedError(
#             "Only super_admin can change status or subscription"
#         )
#     )
#     response = await client.patch(
#         "/api/v1/museums/1", json={"subscription_plan": "premium"}
#     )
#     assert response.status_code == 403
#
#
# async def test_delete_museum(client: AsyncClient, mock_museum_service):
#     mock_museum_service.delete = AsyncMock(return_value=None)
#     response = await client.delete("/api/v1/museums/1")
#     assert response.status_code == 204
#     mock_museum_service.delete.assert_called_once_with(1)
#
#
# async def test_delete_museum_not_found(client: AsyncClient, mock_museum_service):
#     mock_museum_service.delete = AsyncMock(
#         side_effect=NotFoundError("Museum not found")
#     )
#     response = await client.delete("/api/v1/museums/999")
#     assert response.status_code == 404
