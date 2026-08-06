import asyncio
import logging

import redis.asyncio as aioredis

from app.config.settings import settings
from app.infrastructure.messaging.celery_app import celery_app
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService
from app.infrastructure.messaging.notification_queue import NotificationQueue
from app.infrastructure.messaging.event_handlers import _send_with_retry

logger = logging.getLogger(__name__)


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
