from fastapi import APIRouter, Depends, Request, Response, status, Query

from app.api.dependencies import get_session_service, get_current_admin_user
from app.core.config import settings
from app.services.session import SessionService
from app.db.models import AdminUser
from app.exceptions.session import TerminateCurrentSessionError
from app.schemas.session import SessionListResponse

router = APIRouter(prefix="/admin/sessions", tags=["Session"])

@router.get(
    "",
    response_model=SessionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить активные сессии"
)
async def get_sessions(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        current_user: AdminUser = Depends(get_current_admin_user),
        service: SessionService = Depends(get_session_service),
):
    sessions = await service.get_active_sessions(current_user.id, offset, limit)
    return SessionListResponse(items=sessions)

@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Завершить сессию по id"
)
async def terminate_session(
        request: Request,
        session_id: str,
        current_user: AdminUser = Depends(get_current_admin_user),
        service: SessionService = Depends(get_session_service),
) -> Response:
    current_session_id = request.cookies.get(settings.SESSION_COOKIE)
    if session_id == current_session_id:
        raise TerminateCurrentSessionError()

    session_data = await service.get_session(session_id)
    if session_data and session_data.get("user_id") == current_user.id:
        await service.invalidate_session(session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

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


