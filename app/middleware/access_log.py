import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("access")

SKIP_LOG_PATHS = {
    "/health",
    "/api/v1/docs",
    "/api/v1/redoc",
    "/api/v1/openapi.json",
}

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()

        response = await call_next(request)

        path = request.url.path

        if path in SKIP_LOG_PATHS:
            return response

        duration_ms = round((time.time() - start) * 1000, 3)

        logger.info(
            "http_request",
            extra={
                "method": request.method,
                "status_code": response.status_code,
                "path": request.url.path,
                "duration_ms": duration_ms,
                "request_id": request.state.request_id,
            },
        )

        return response