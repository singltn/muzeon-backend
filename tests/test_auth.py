# import pytest
# from httpx import AsyncClient
#
# from app.api.dependencies import get_auth_service, get_current_user
# from app.core.exceptions import AuthenticationError, BadRequestError
# from app.enums.database import UserRoleEnum
# from app.main import app
# from app.schemas.auth import CurrentUserResponse
#
#
# async def test_login_success(client: AsyncClient, mock_auth_service):
#     response = await client.post(
#         "/api/v1/auth/login",
#         json={"email": "admin@muzeon.ru", "password": "password123"},
#     )
#     assert response.status_code == 200
#     assert response.json()["message"] == "OTP code sent to your email"
#     mock_auth_service.initiate_login.assert_called_once_with(
#         "admin@muzeon.ru", "password123"
#     )
#
#
# async def test_login_invalid_credentials(client: AsyncClient, mock_auth_service):
#     mock_auth_service.initiate_login.side_effect = AuthenticationError(
#         "Invalid email or password"
#     )
#     response = await client.post(
#         "/api/v1/auth/login",
#         json={"email": "wrong@test.com", "password": "wrong"},
#     )
#     assert response.status_code == 401
#     assert "Invalid email or password" in response.json()["detail"]
#
#
# async def test_login_inactive_account(client: AsyncClient, mock_auth_service):
#     mock_auth_service.initiate_login.side_effect = AuthenticationError(
#         "Account is inactive"
#     )
#     response = await client.post(
#         "/api/v1/auth/login",
#         json={"email": "inactive@test.com", "password": "pass"},
#     )
#     assert response.status_code == 401
#
#
# async def test_verify_otp_success(
#     client: AsyncClient, mock_auth_service, super_admin: CurrentUserResponse
# ):
#     mock_auth_service.verify_otp.return_value = "test_session_id"
#     mock_auth_service.get_current_user.return_value = super_admin
#
#     response = await client.post(
#         "/api/v1/auth/verify",
#         json={"email": "admin@muzeon.ru", "otp": "123456"},
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["email"] == super_admin.email
#     assert data["role"] == UserRoleEnum.super_admin
#     assert "session_id" in response.cookies
#
#
# async def test_verify_otp_invalid_code(client: AsyncClient, mock_auth_service):
#     mock_auth_service.verify_otp.side_effect = BadRequestError("Invalid OTP code")
#     response = await client.post(
#         "/api/v1/auth/verify",
#         json={"email": "admin@muzeon.ru", "otp": "000000"},
#     )
#     assert response.status_code == 400
#     assert "Invalid OTP code" in response.json()["detail"]
#
#
# async def test_verify_otp_expired(client: AsyncClient, mock_auth_service):
#     mock_auth_service.verify_otp.side_effect = BadRequestError(
#         "OTP expired or not requested"
#     )
#     response = await client.post(
#         "/api/v1/auth/verify",
#         json={"email": "admin@muzeon.ru", "otp": "111111"},
#     )
#     assert response.status_code == 400
#
#
# async def test_verify_otp_too_many_attempts(client: AsyncClient, mock_auth_service):
#     mock_auth_service.verify_otp.side_effect = BadRequestError(
#         "Too many attempts — please log in again"
#     )
#     response = await client.post(
#         "/api/v1/auth/verify",
#         json={"email": "admin@muzeon.ru", "otp": "999999"},
#     )
#     assert response.status_code == 400
#
#
# async def test_get_me(client: AsyncClient, super_admin: CurrentUserResponse):
#     response = await client.get("/api/v1/auth/me")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == super_admin.id
#     assert data["email"] == super_admin.email
#     assert data["role"] == UserRoleEnum.super_admin
#     assert data["museum_id"] is None
#
#
# async def test_get_me_unauthenticated(client: AsyncClient):
#     app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(
#         AuthenticationError("Not authenticated")
#     )
#     try:
#         response = await client.get("/api/v1/auth/me")
#         assert response.status_code == 401
#     finally:
#         from app.schemas.auth import CurrentUserResponse
#         from app.enums.database import UserRoleEnum
#         super_admin = CurrentUserResponse(
#             id=1, email="admin@muzeon.ru", first_name="Super", last_name="Admin",
#             role=UserRoleEnum.super_admin, museum_id=None,
#         )
#         app.dependency_overrides[get_current_user] = lambda: super_admin
#
#
# async def test_logout(client: AsyncClient, mock_auth_service):
#     response = await client.post(
#         "/api/v1/auth/logout",
#         cookies={"session_id": "some_session_id"},
#     )
#     assert response.status_code == 204
#     mock_auth_service.logout.assert_called_once_with("some_session_id")
#
#
# async def test_logout_without_session(client: AsyncClient, mock_auth_service):
#     response = await client.post("/api/v1/auth/logout")
#     assert response.status_code == 204
#     mock_auth_service.logout.assert_not_called()
