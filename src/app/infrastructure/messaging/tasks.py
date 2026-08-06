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


@celery_app.task(name="notify_completed_expeditions")
def notify_completed_expeditions():
    return asyncio.run(_async_notify_completed_expeditions())


async def _async_notify_completed_expeditions() -> int:
    from datetime import datetime, timezone

    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    notified_count = 0

    try:
        async with async_session() as session:
            rows = await session.execute(
                text(
                    "SELECT e.id, e.ship_id, p.telegram_id, z.name AS zone_name "
                    "FROM expeditions e "
                    "JOIN ships s ON s.id = e.ship_id "
                    "JOIN players p ON p.id = s.player_id "
                    "JOIN zones z ON z.id = e.zone_id "
                    "WHERE e.status = 'finished' AND e.notified_at IS NULL"
                )
            )
            expeditions_to_notify = rows.fetchall()

            if not expeditions_to_notify:
                return 0

            bot = TelegramBotService()
            app_url = settings.PUBLIC_URL

            for expedition_id, ship_id, telegram_id, zone_name in expeditions_to_notify:
                try:
                    text_msg = (
                        f"🚀 Капитан, экспедиция из зоны \"{zone_name}\" завершена!\n\n"
                        f"Заберите награду в ангаре."
                    )
                    reply_markup = {
                        "inline_keyboard": [[
                            {
                                "text": "Открыть ангар",
                                "url": f"{app_url}?startapp=open_hangar",
                            }
                        ]]
                    }

                    sent = await bot.send_message(
                        chat_id=telegram_id,
                        text=text_msg,
                        reply_markup=reply_markup,
                    )

                    if sent:
                        await session.execute(
                            text(
                                "UPDATE expeditions "
                                "SET notified_at = :now "
                                "WHERE id = :id"
                            ),
                            {"id": expedition_id, "now": datetime.now(timezone.utc)},
                        )
                        await session.commit()
                        notified_count += 1
                        logger.info(
                            "Notified player %s about expedition %s",
                            telegram_id,
                            expedition_id,
                        )
                    else:
                        logger.warning(
                            "Failed to send notification for expedition %s to %s, marking as notified to stop retries",
                            expedition_id,
                            telegram_id,
                        )
                        await session.execute(
                            text(
                                "UPDATE expeditions SET notified_at = :now WHERE id = :id"
                            ),
                            {"id": expedition_id, "now": datetime.now(timezone.utc)},
                        )
                        await session.commit()
                except Exception:
                    logger.exception(
                        "Error notifying expedition %s", expedition_id
                    )

        return notified_count
    except Exception:
        logger.exception("Failed to run notify_completed_expeditions")
        return 0
    finally:
        await engine.dispose()
