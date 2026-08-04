import logging

import sentry_sdk
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class SentryUserMiddleware(BaseHTTPMiddleware):
    """Extracts telegram_id from Authorization header and binds it to Sentry scope.
    Only runs when Sentry is initialized (DSN is configured).
    """

    async def dispatch(self, request: Request, call_next):
        authorization = request.headers.get("authorization", "")
        if authorization.startswith("tghash "):
            try:
                from app.infrastructure.security.telegram_auth import (
                    verify_telegram_init_data,
                )
                from app.config.settings import settings

                init_data = authorization[len("tghash "):]
                telegram_user = verify_telegram_init_data(
                    init_data, settings.BOT_TOKEN
                )
                sentry_sdk.set_user({"id": telegram_user.telegram_id})
            except Exception:
                logger.debug("Failed to extract telegram_id for Sentry user context")

        response = await call_next(request)
        sentry_sdk.set_user(None)
        return response
