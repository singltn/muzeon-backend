# from unittest.mock import AsyncMock
#
# import pytest
# import pytest_asyncio
# from httpx import ASGITransport, AsyncClient
#
# from app.api.dependencies import (
#     get_auth_service,
#     get_current_user,
#     get_museum_service,
#     get_user_service,
# )
# from app.enums.database import UserRoleEnum
# from app.main import app
# from app.schemas.auth import CurrentUserResponse
# from app.services.auth import AuthService
# from app.services.museum import MuseumService
# from app.services.user import UserService
#
#
# @pytest.fixture
# def super_admin() -> CurrentUserResponse:
#     return CurrentUserResponse(
#         id=1,
#         email="admin@muzeon.ru",
#         first_name="Super",
#         last_name="Admin",
#         role=UserRoleEnum.super_admin,
#         museum_id=None,
#     )
#
#
# @pytest.fixture
# def museum_admin() -> CurrentUserResponse:
#     return CurrentUserResponse(
#         id=2,
#         email="museum@muzeon.ru",
#         first_name="Museum",
#         last_name="Admin",
#         role=UserRoleEnum.museum_admin,
#         museum_id=1,
#     )
#
#
# @pytest.fixture
# def mock_auth_service() -> AsyncMock:
#     service = AsyncMock(spec=AuthService)
#     service.initiate_login = AsyncMock()
#     service.verify_otp = AsyncMock(return_value="test_session_id")
#     service.logout = AsyncMock()
#     return service
#
#
# @pytest.fixture
# def mock_museum_service() -> AsyncMock:
#     return AsyncMock(spec=MuseumService)
#
#
# @pytest.fixture
# def mock_user_service() -> AsyncMock:
#     return AsyncMock(spec=UserService)
#
#
# @pytest_asyncio.fixture
# async def client(
#     mock_auth_service: AsyncMock,
#     mock_museum_service: AsyncMock,
#     mock_user_service: AsyncMock,
#     super_admin: CurrentUserResponse,
# ):
#     app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
#     app.dependency_overrides[get_museum_service] = lambda: mock_museum_service
#     app.dependency_overrides[get_user_service] = lambda: mock_user_service
#     app.dependency_overrides[get_current_user] = lambda: super_admin
#
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as ac:
#         yield ac
#
#     app.dependency_overrides.clear()
