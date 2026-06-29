import asyncio
import logging

from celery import Celery
from celery.schedules import crontab
from sqlalchemy.ext.asyncio import AsyncSession

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

logger = logging.getLogger(__name__)

celery_app = Celery(
    "hitchhiker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.beat_schedule = {
    "check-finished-expeditions-every-60s": {
        "task": "app.infrastructure.messaging.celery_app.check_finished_expeditions",
        "schedule": 60.0,
    },
}

celery_app.conf.timezone = "UTC"


async def _run_check_finished_expeditions() -> int:
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