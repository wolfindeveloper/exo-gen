import logging
import uuid
from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time()

        request.state.request_id = request_id
        logger.debug("Request %s: %s %s", request_id, request.method, request.url.path)

        response: Response = await call_next(request)

        elapsed = time() - start
        response.headers["X-Request-ID"] = request_id
        logger.debug(
            "Request %s completed: %s %s -> %s (%.2fms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed * 1000,
        )

        return response
