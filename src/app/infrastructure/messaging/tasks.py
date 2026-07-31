import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import redis.asyncio as aioredis

from app.config.settings import settings
from app.infrastructure.messaging.celery_app import celery_app
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService
from app.infrastructure.messaging.notification_queue import NotificationQueue
from app.infrastructure.messaging.event_handlers import _send_with_retry

logger = logging.getLogger(__name__)


@celery_app.task(name="finish_expedition")
def finish_expedition_task(expedition_id: str, player_telegram_id: int):
    asyncio.run(_async_finish_expedition(expedition_id, player_telegram_id))


async def _async_finish_expedition(expedition_id: str, player_telegram_id: int):
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
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

            await session.execute(
                text(
                    "UPDATE expeditions SET status = :status WHERE id = :id AND status = 'in_progress'"
                ),
                {"status": "finished", "id": expedition_id},
            )
            await session.commit()
            logger.info("Expedition %s auto-finished", expedition_id)

            bot = TelegramBotService()
            await bot.send_message(
                chat_id=player_telegram_id,
                text=(
                    "<b>Expedition Complete!</b>\n\n"
                    "Your ship has returned from the expedition.\n"
                    "Head to the game to claim your rewards!"
                ),
            )
    except Exception:
        logger.exception("Failed to finish expedition %s", expedition_id)
    finally:
        await engine.dispose()


@celery_app.task(name="process_notification_queue")
def process_notification_queue_task():
    return asyncio.run(_async_process_notification_queue())


async def _async_process_notification_queue():
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    queue = NotificationQueue(redis)
    bot = TelegramBotService()

    processed = 0
    try:
        while True:
            notification = await queue.dequeue()
            if not notification:
                break

            sent = await _send_with_retry(
                bot, notification["chat_id"], notification["text"]
            )
            if not sent:
                new_retry = notification.get("retry_count", 0) + 1
                if new_retry >= NotificationQueue.MAX_RETRIES:
                    await queue.move_to_dlq(notification)
                    logger.error(
                        f"Notification permanently failed: chat_id={notification['chat_id']}"
                    )
                else:
                    await queue.enqueue(
                        notification["chat_id"],
                        notification["text"],
                        retry_count=new_retry,
                    )
                    logger.info(
                        f"Re-enqueued notification: chat_id={notification['chat_id']} "
                        f"(retry={new_retry}/{NotificationQueue.MAX_RETRIES})"
                    )
            processed += 1
    except Exception:
        logger.exception("Failed to process notification queue")
    finally:
        await redis.close()

    return processed
