"""EXO GENESIS — FastAPI application entry point."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from core.config import settings
from core.database import close_engine, init_db, test_connection as test_db
from core.redis import close_redis, test_connection as test_redis

logger = logging.getLogger("exo_genesis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup/shutdown lifecycle: connect DB and Redis."""
    logger.info("Starting EXO GENESIS API (env=%s)", settings.app_env)

    db_ok = await test_db()
    logger.info("Database connection: %s", "OK" if db_ok else "SKIPPED (unavailable)")

    if db_ok:
        await init_db()

    redis_ok = await test_redis()
    logger.info("Redis connection: %s", "OK" if redis_ok else "SKIPPED (unavailable)")

    yield

    logger.info("Shutting down EXO GENESIS API")
    await close_redis()
    await close_engine()


app = FastAPI(
    title="EXO GENESIS",
    version="0.1.0",
    description="TON-based Telegram Mini App game backend",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (после CORS, перед роутерами)
from api.middleware.rate_limit import rate_limit_middleware

app.middleware("http")(rate_limit_middleware)


@app.middleware("http")
async def request_logging(request: Request, call_next) -> Response:
    """Log every request with method, path, status code, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"status": "running", "service": "exo-genesis-api"}


@app.get("/health")
async def health() -> dict[str, bool | str]:
    """Health check with DB and Redis status."""
    db_ok = await test_db()
    redis_ok = await test_redis()
    return {
        "ok": db_ok and redis_ok,
        "database": db_ok,
        "redis": redis_ok,
        "env": settings.app_env,
    }


from api.routers import artifacts, auth, configs, expeditions, laboratory, player, resources, wallet

app.include_router(auth.router)
app.include_router(player.router)
app.include_router(configs.router)
app.include_router(expeditions.router)
app.include_router(laboratory.router)
app.include_router(artifacts.router)
app.include_router(wallet.router)
app.include_router(resources.router)
