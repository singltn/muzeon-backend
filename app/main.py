from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.redis import close_redis, init_redis
from app.db.session import close_db
from app.middleware.request_id import RequestIDMiddleware
from app.exceptions.base import AppException
from app.exceptions import app_exception_handler, validation_exception_handler
from app.core.logging import setup_logging
from app.middleware.access_log import AccessLogMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()
    await close_db()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="MUZEON API",
        version=settings.VERSION,
        openapi_url=f'{settings.URL_PREFIX}/openapi.json',
        docs_url=f'{settings.URL_PREFIX}/docs',
        redoc_url=f'{settings.URL_PREFIX}/redoc',
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_exception_handler(
        AppException,
        app_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
