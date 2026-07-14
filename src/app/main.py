import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from redis.asyncio import Redis

from app.config.settings import settings
from app.presentation.api.routes.player import router as player_router
from app.presentation.api.routes.admin import router as admin_router
from app.presentation.api.routes.zones import router as zones_router
from app.presentation.api.routes.expeditions import router as expeditions_router
from app.presentation.api.routes.guide import router as guide_router
from app.presentation.api.routes.inventory import router as inventory_router
from app.presentation.api.routes.equipment import router as equipment_router
from app.presentation.api.routes.ships import router as ships_router
from app.presentation.api.routes.shop import router as shop_router
from app.presentation.api.routes.payments import router as payments_router
from app.presentation.api.routes.leaderboard import router as leaderboard_router
from app.presentation.api.routes.settings import router as settings_router
from app.infrastructure.cache.redis_client import redis_client
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService
from app.infrastructure.messaging.event_handlers import setup_event_handlers
from app.infrastructure.security.rate_limiter import limiter
from app.infrastructure.middleware.request_id import RequestIDMiddleware
from app.domain.exceptions import DomainError
from app.domain.exceptions.inventory import NoSuitableConsumableError
from app.domain.exceptions.player import InsufficientXgenError, InsufficientFragmentsError
from app.domain.exceptions.zone import ZoneLockedByLevelError
from app.domain.exceptions.equipment import SlotLockedByLevelError


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Hitchhiker's Idle...")

    bot_service = TelegramBotService()
    setup_event_handlers(bot_service)

    webhook_url = f"{settings.PUBLIC_URL.rstrip('/')}/payments/stars/webhook"
    result = await bot_service.set_webhook(
        webhook_url,
        secret_token=settings.TELEGRAM_WEBHOOK_SECRET,
    )
    if result:
        logger.info(f"Telegram webhook set to {webhook_url}")
    else:
        logger.warning(f"Failed to set Telegram webhook at {webhook_url}")

    await redis_client.connect()
    logger.info("Redis connected")

    yield

    await redis_client.disconnect()
    logger.info("Redis disconnected")
    logger.info("Shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Don't Panic. Just idle through the galaxy.",
        version="0.1.0",
        lifespan=lifespan
    )

    # Request ID middleware (first — generates ID for all subsequent middleware)
    app.add_middleware(RequestIDMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=r"^https?://(.*\.)?(exo-gen\.com|telegram\.org|localhost)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # Routes
    app.include_router(player_router)
    app.include_router(admin_router)
    app.include_router(zones_router)
    app.include_router(expeditions_router)
    app.include_router(guide_router)
    app.include_router(inventory_router)
    app.include_router(equipment_router)
    app.include_router(ships_router)
    app.include_router(shop_router)
    app.include_router(payments_router)
    app.include_router(leaderboard_router)
    app.include_router(settings_router)

    # System endpoints
    @app.get("/healthcheck", tags=["System"])
    async def healthcheck():
        return {"status": "ok", "message": "Mostly Harmless"}

    @app.get("/healthcheck/redis", tags=["System"])
    async def healthcheck_redis():
        try:
            redis = Redis.from_url(settings.redis_url, socket_connect_timeout=3)
            await redis.ping()
            await redis.close()
            return {"status": "ok"}
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"status": "error", "detail": str(e)},
            )

    # Global exception handlers
    @app.exception_handler(NoSuitableConsumableError)
    async def no_consumable_handler(request: Request, exc: NoSuitableConsumableError):
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "error_code": "NO_CONSUMABLE",
                "required_effect": exc.effect_key,
                "redirect_to": "shop",
            },
        )

    @app.exception_handler(InsufficientXgenError)
    async def insufficient_xgen_handler(request: Request, exc: InsufficientXgenError):
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "error_code": "INSUFFICIENT_XGEN",
                "required": exc.required,
                "available": exc.available,
                "redirect_to": "shop",
            },
        )

    @app.exception_handler(InsufficientFragmentsError)
    async def insufficient_fragments_handler(request: Request, exc: InsufficientFragmentsError):
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "error_code": "INSUFFICIENT_FRAGMENTS",
                "required": exc.required,
                "available": exc.available,
                "redirect_to": "shop",
            },
        )

    @app.exception_handler(ZoneLockedByLevelError)
    async def zone_locked_handler(request: Request, exc: ZoneLockedByLevelError):
        return JSONResponse(
            status_code=403,
            content={
                "detail": str(exc),
                "error_code": "ZONE_LOCKED_BY_LEVEL",
                "required_level": exc.required_level,
                "current_level": exc.current_level,
            },
        )

    @app.exception_handler(SlotLockedByLevelError)
    async def slot_locked_handler(request: Request, exc: SlotLockedByLevelError):
        return JSONResponse(
            status_code=403,
            content={
                "detail": str(exc),
                "error_code": "SLOT_LOCKED_BY_LEVEL",
                "required_level": exc.required_level,
                "current_level": exc.current_level,
                "max_slots": exc.max_slots,
            },
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        retry_after = None
        if hasattr(exc, "retry_after") and exc.retry_after:
            retry_after = str(exc.retry_after)
        headers = {}
        if retry_after:
            headers["Retry-After"] = retry_after
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Try again later."},
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app

app = create_app()