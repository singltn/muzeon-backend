from fastapi import APIRouter

from app.api.v1.endpoints.admin import users, auth, session, museums, museum_users, events
from app.core.config import settings
api_router = APIRouter(prefix=settings.URL_PREFIX)

api_router.include_router(auth.router)
api_router.include_router(museums.router)
api_router.include_router(museum_users.router)
api_router.include_router(events.router)
api_router.include_router(users.router)
api_router.include_router(session.router)
