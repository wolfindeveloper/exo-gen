import asyncio
import logging

from app.domain.events.dispatcher import dispatcher
from app.domain.events.player_events import (
    ExpeditionCompletedEvent,
    ChapterCompletedEvent,
    DailyLoginCompletedEvent,
    ArticleUnlockedEvent,
)
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService
from app.infrastructure.messaging.notification_queue import NotificationQueue

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_DELAY = 1.0


async def _send_with_retry(
    bot_service: TelegramBotService,
    chat_id: int,
    text: str,
    max_retries: int = MAX_RETRIES,
) -> bool:
    """Send message with retry and exponential backoff."""
    for attempt in range(max_retries):
        try:
            success = await bot_service.send_message(chat_id, text)
            if success:
                return True
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed for chat_id={chat_id}"
            )
        except Exception as e:
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} exception for chat_id={chat_id}: {e}"
            )

        if attempt < max_retries - 1:
            delay = BASE_DELAY * (2 ** attempt)
            logger.info(f"Retrying in {delay}s...")
            await asyncio.sleep(delay)

    logger.error(f"All {max_retries} attempts failed for chat_id={chat_id}")
    return False


def create_expedition_completed_handler(
    bot_service: TelegramBotService,
    notification_queue: NotificationQueue | None = None,
):
    async def handler(event: ExpeditionCompletedEvent) -> None:
        text = (
            "🚀 <b>Экспедиция завершена!</b>\n\n"
            "Твой корабль вернулся из зоны.\n"
            "Зайди в игру, чтобы забрать награду!"
        )
        sent = await _send_with_retry(bot_service, event.telegram_id, text)
        if not sent and notification_queue:
            await notification_queue.enqueue(event.telegram_id, text)

    return handler


def create_chapter_completed_handler(
    bot_service: TelegramBotService,
    notification_queue: NotificationQueue | None = None,
):
    async def handler(event: ChapterCompletedEvent) -> None:
        text = (
            f"📖 <b>Глава завершена!</b>\n\n"
            f"Поздравляем! Ты открыл все статьи в главе.\n"
            f"💰 Награда: {event.xgen_rewarded} XGen + {event.fragments_rewarded} фрагментов\n"
            f"🎁 Бонусный бокс уже в инвентаре!"
        )
        sent = await _send_with_retry(bot_service, event.telegram_id, text)
        if not sent and notification_queue:
            await notification_queue.enqueue(event.telegram_id, text)

    return handler


def create_daily_login_handler(
    bot_service: TelegramBotService,
    notification_queue: NotificationQueue | None = None,
):
    async def handler(event: DailyLoginCompletedEvent) -> None:
        if event.got_box:
            text = (
                f"🎁 <b>Поздравляем!</b>\n\n"
                f"Твой стрик: {event.new_streak} дней!\n"
                f"Ты получил бонусный бокс за преданность.\n"
                f"Зайди в игру, чтобы открыть его!"
            )
            sent = await _send_with_retry(bot_service, event.telegram_id, text)
            if not sent and notification_queue:
                await notification_queue.enqueue(event.telegram_id, text)

    return handler


def create_article_unlocked_handler(
    bot_service: TelegramBotService,
    notification_queue: NotificationQueue | None = None,
):
    async def handler(event: ArticleUnlockedEvent) -> None:
        pass

    return handler


def setup_event_handlers(
    bot_service: TelegramBotService,
    notification_queue: NotificationQueue | None = None,
) -> None:
    dispatcher.register(
        ExpeditionCompletedEvent,
        create_expedition_completed_handler(bot_service, notification_queue),
    )
    dispatcher.register(
        ChapterCompletedEvent,
        create_chapter_completed_handler(bot_service, notification_queue),
    )
    dispatcher.register(
        DailyLoginCompletedEvent,
        create_daily_login_handler(bot_service, notification_queue),
    )
    dispatcher.register(
        ArticleUnlockedEvent,
        create_article_unlocked_handler(bot_service, notification_queue),
    )
    logger.info("Event handlers registered successfully")
