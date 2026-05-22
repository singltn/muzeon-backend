# from datetime import datetime, timezone
# from unittest.mock import AsyncMock, MagicMock
#
# import pytest
# from httpx import AsyncClient
#
# from app.api.dependencies import get_current_user
# from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
# from app.enums.database import UserRoleEnum
# from app.main import app
# from app.schemas.auth import CurrentUserResponse
#
# USER_PAYLOAD = {
#     "email": "staff@hermitage.ru",
#     "password": "staffpass123",
#     "first_name": "Анна",
#     "last_name": "Петрова",
#     "role": "content",
# }
#
#
# def _make_user(user_id: int = 10, museum_id: int = 1) -> MagicMock:
#     u = MagicMock()
#     u.id = user_id
#     u.email = "staff@hermitage.ru"
#     u.first_name = "Анна"
#     u.last_name = "Петрова"
#     u.role = UserRoleEnum.content
#     u.is_active = True
#     u.museum_id = museum_id
#     u.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
#     u.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
#     return u
#
#
# async def test_create_user(client: AsyncClient, mock_user_service):
#     mock_user_service.create = AsyncMock(return_value=_make_user())
#     response = await client.post("/api/v1/museums/1/users", json=USER_PAYLOAD)
#     assert response.status_code == 201
#     data = response.json()
#     assert data["email"] == "staff@hermitage.ru"
#     assert data["role"] == UserRoleEnum.content
#
#
# async def test_create_user_duplicate_email(client: AsyncClient, mock_user_service):
#     mock_user_service.create = AsyncMock(
#         side_effect=ConflictError("User with this email already exists")
#     )
#     response = await client.post("/api/v1/museums/1/users", json=USER_PAYLOAD)
#     assert response.status_code == 409
#
#
# async def test_create_user_forbidden_wrong_museum(
#     client: AsyncClient, mock_user_service
# ):
#     mock_user_service.create = AsyncMock(
#         side_effect=PermissionDeniedError("Access denied to this museum")
#     )
#     response = await client.post("/api/v1/museums/99/users", json=USER_PAYLOAD)
#     assert response.status_code == 403
#
#
# async def test_create_user_cannot_set_super_admin_role(
#     client: AsyncClient, mock_user_service
# ):
#     mock_user_service.create = AsyncMock(
#         side_effect=PermissionDeniedError("Cannot create super_admin through this endpoint")
#     )
#     payload = {**USER_PAYLOAD, "role": "super_admin"}
#     response = await client.post("/api/v1/museums/1/users", json=payload)
#     assert response.status_code == 403
#
#
# async def test_create_museum_admin_requires_super_admin(
#     client: AsyncClient, mock_user_service, museum_admin: CurrentUserResponse
# ):
#     app.dependency_overrides[get_current_user] = lambda: museum_admin
#     mock_user_service.create = AsyncMock(
#         side_effect=PermissionDeniedError("Only super_admin can assign museum_admin role")
#     )
#     try:
#         payload = {**USER_PAYLOAD, "role": "museum_admin"}
#         response = await client.post("/api/v1/museums/1/users", json=payload)
#         assert response.status_code == 403
#     finally:
#         super_admin = CurrentUserResponse(
#             id=1, email="admin@muzeon.ru", first_name="Super", last_name="Admin",
#             role=UserRoleEnum.super_admin, museum_id=None,
#         )
#         app.dependency_overrides[get_current_user] = lambda: super_admin
#
#
# async def test_list_users(client: AsyncClient, mock_user_service):
#     users = [_make_user(i) for i in range(10, 13)]
#     mock_user_service.list_by_museum = AsyncMock(return_value=(users, 3))
#
#     response = await client.get("/api/v1/museums/1/users")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["total"] == 3
#     assert len(data["items"]) == 3
#
#
# async def test_list_users_pagination(client: AsyncClient, mock_user_service):
#     mock_user_service.list_by_museum = AsyncMock(return_value=([], 0))
#     response = await client.get("/api/v1/museums/1/users?offset=10&limit=5")
#     assert response.status_code == 200
#     call_args = mock_user_service.list_by_museum.call_args
#     assert call_args.args[:3] == (1, 10, 5)
#
#
# async def test_get_user(client: AsyncClient, mock_user_service):
#     mock_user_service.get = AsyncMock(return_value=_make_user())
#     response = await client.get("/api/v1/museums/1/users/10")
#     assert response.status_code == 200
#     assert response.json()["id"] == 10
#
#
# async def test_get_user_not_found(client: AsyncClient, mock_user_service):
#     mock_user_service.get = AsyncMock(side_effect=NotFoundError("User not found"))
#     response = await client.get("/api/v1/museums/1/users/999")
#     assert response.status_code == 404
#
#
# async def test_update_user(client: AsyncClient, mock_user_service):
#     updated = _make_user()
#     updated.first_name = "Мария"
#     mock_user_service.update = AsyncMock(return_value=updated)
#
#     response = await client.patch(
#         "/api/v1/museums/1/users/10", json={"first_name": "Мария"}
#     )
#     assert response.status_code == 200
#
#
# async def test_update_user_not_found(client: AsyncClient, mock_user_service):
#     mock_user_service.update = AsyncMock(side_effect=NotFoundError("User not found"))
#     response = await client.patch(
#         "/api/v1/museums/1/users/999", json={"first_name": "Test"}
#     )
#     assert response.status_code == 404
#
#
# async def test_delete_user(client: AsyncClient, mock_user_service):
#     mock_user_service.delete = AsyncMock(return_value=None)
#     response = await client.delete("/api/v1/museums/1/users/10")
#     assert response.status_code == 204
#     mock_user_service.delete.assert_called_once()
#
#
# async def test_delete_user_not_found(client: AsyncClient, mock_user_service):
#     mock_user_service.delete = AsyncMock(side_effect=NotFoundError("User not found"))
#     response = await client.delete("/api/v1/museums/1/users/999")
#     assert response.status_code == 404
