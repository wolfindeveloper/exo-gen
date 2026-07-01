import asyncio
import logging

from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config.settings import settings
from app.infrastructure.messaging.celery_app import celery_app
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService

logger = logging.getLogger(__name__)


@celery_app.task(name="finish_expedition")
def finish_expedition_task(expedition_id: str, player_telegram_id: int):
    asyncio.run(_async_finish_expedition(expedition_id, player_telegram_id))


async def _async_finish_expedition(expedition_id: str, player_telegram_id: int):
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # 1. Check expedition exists and is still in_progress
            result = await session.execute(
                text("SELECT status FROM expeditions WHERE id = :id"),
                {"id": expedition_id},
            )
            row = result.fetchone()
            if row is None:
                logger.warning("Expedition %s not found, skipping", expedition_id)
                return

            if row[0] != "in_progress":
                logger.info(
                    "Expedition %s already %s, skipping", expedition_id, row[0]
                )
                return

            # 2. Update status to finished
            now = datetime.now(timezone.utc)
            await session.execute(
                text(
                    "UPDATE expeditions SET status = :status WHERE id = :id AND status = 'in_progress'"
                ),
                {"status": "finished", "id": expedition_id},
            )
            await session.commit()
            logger.info("Expedition %s auto-finished", expedition_id)

            # 3. Send Telegram notification
            bot = TelegramBotService()
            await bot.send_message(
                chat_id=player_telegram_id,
                text=(
                    f"🚀 <b>Expedition Complete!</b>\n\n"
                    f"Your ship has returned from the expedition.\n"
                    f"Head to the game to claim your rewards!"
                ),
            )
    except Exception:
        logger.exception("Failed to finish expedition %s", expedition_id)
    finally:
        await engine.dispose()
