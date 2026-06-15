from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_admin_user, get_dashboard_service
from app.db.models import AdminUser
from app.exceptions.schemas import ErrorResponse
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/admin/dashboard", tags=["dashboard"])


@router.get(
    "",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Дашборд в зависимости от роли",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Permission denied"},
    },
)
async def get_dashboard(
    current_user: AdminUser = Depends(get_current_admin_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    return await service.get_dashboard(current_user)
