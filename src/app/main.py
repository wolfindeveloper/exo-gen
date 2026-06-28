import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.presentation.api.routes.player import router as player_router
from app.presentation.api.routes.admin import router as admin_router
from app.presentation.api.routes.zones import router as zones_router
from app.presentation.api.routes.expeditions import router as expeditions_router
from app.presentation.api.routes.guide import router as guide_router
from app.presentation.api.routes.inventory import router as inventory_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Hitchhiker's Idle...")
    yield
    logger.info("Shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Don't Panic. Just idle through the galaxy.",
        version="0.1.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В проде ограничим!
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(player_router)
    app.include_router(admin_router)
    app.include_router(zones_router)
    app.include_router(expeditions_router)
    app.include_router(guide_router)
    app.include_router(inventory_router)

    @app.get("/healthcheck", tags=["System"])
    async def healthcheck():
        return {"status": "ok", "message": "Mostly Harmless"}

    return app

app = create_app()