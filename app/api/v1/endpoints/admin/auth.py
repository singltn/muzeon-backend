from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import get_auth_service, get_session_service
from app.core.config import settings
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    VerifyRequest,
)
from app.services.auth import AuthService
from app.services.session import SessionService
from app.exceptions.schemas import ErrorResponse

router = APIRouter(prefix="/admin/auth", tags=["Auth"])

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Аутентификация администратора",
    description="Проверка пользователя и отправка OTP",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid credentials",
        },
        403: {
            "model": ErrorResponse,
            "description": "Account is inactive",
        },
        422: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
    }
)
async def login(
        payload: LoginRequest,
        service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    await service.initiate_login(payload.email, payload.password)
    return LoginResponse(message="OTP code sent")


@router.post(
     "/verify",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="2FA email",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid OTP code",
        },
        401: {
            "model": ErrorResponse,
            "description": "Session expired",
        },
    }
)
async def verify_otp(
        payload: VerifyRequest,
        request: Request,
        response: Response,
        service: AuthService = Depends(get_auth_service),
) -> Response:
    session_id = await service.verify_otp(
        payload.email,
        payload.otp,
        request.client.host,
        request.headers.get("user-agent")
    )

    response.set_cookie(
        key=settings.SESSION_COOKIE,
        value=session_id,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=settings.SESSION_TTL,
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

@router.post("/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout"
)
async def logout(
        request: Request,
        response: Response,
        service: SessionService = Depends(get_session_service),
) -> Response:
    session_id = request.cookies.get(settings.SESSION_COOKIE)
    if session_id:
        await service.invalidate_session(session_id)
    response.delete_cookie(settings.SESSION_COOKIE)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
