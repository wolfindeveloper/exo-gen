import asyncio
import logging

import redis.asyncio as aioredis
from celery import Celery

from app.config.settings import settings
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.persistence.repositories.sqlalchemy_expedition_repository import (
    SQLAlchemyExpeditionRepository,
)
from app.infrastructure.persistence.repositories.sqlalchemy_player_repository import (
    SQLAlchemyPlayerRepository,
)
from app.infrastructure.persistence.uow import SQLAlchemyUnitOfWork
from app.application.use_cases.process_finished_expeditions import (
    ProcessFinishedExpeditionsUseCase,
)
from app.infrastructure.messaging.event_handlers import setup_event_handlers
from app.infrastructure.messaging.notification_queue import NotificationQueue
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService

logger = logging.getLogger(__name__)

_handlers_registered = False


def _ensure_event_handlers_registered() -> None:
    """Register domain event handlers in the worker process (dispatch happens here)."""
    global _handlers_registered
    if _handlers_registered:
        return
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    setup_event_handlers(
        TelegramBotService(),
        NotificationQueue(redis),
    )
    _handlers_registered = True

celery_app = Celery(
    "hitchhiker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.beat_schedule = {
    "check-finished-expeditions-every-60s": {
        "task": "check_finished_expeditions",
        "schedule": 60.0,
    },
    "process-notification-queue-every-30s": {
        "task": "process_notification_queue",
        "schedule": 30.0,
    },
}

celery_app.conf.timezone = "UTC"
celery_app.conf.task_track_started = True


async def _run_check_finished_expeditions() -> int:
    _ensure_event_handlers_registered()
    async with AsyncSessionLocal() as session:
        uow = SQLAlchemyUnitOfWork(session)
        expedition_repo = SQLAlchemyExpeditionRepository(session)
        player_repo = SQLAlchemyPlayerRepository(session)

        use_case = ProcessFinishedExpeditionsUseCase(
            expedition_repo=expedition_repo,
            player_repo=player_repo,
        )

        count = await use_case.execute(uow)
        return count


@celery_app.task(name="check_finished_expeditions")
def check_finished_expeditions() -> int:
    count = asyncio.run(_run_check_finished_expeditions())
    if count:
        logger.info("Finished %s expeditions", count)
    return count