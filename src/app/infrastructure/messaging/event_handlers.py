import logging

from app.domain.events.dispatcher import dispatcher
from app.domain.events.player_events import (
    ExpeditionCompletedEvent,
    ChapterCompletedEvent,
    DailyLoginCompletedEvent,
    ArticleUnlockedEvent,
)
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService

logger = logging.getLogger(__name__)


def create_expedition_completed_handler(bot_service: TelegramBotService):
    async def handler(event: ExpeditionCompletedEvent) -> None:
        try:
            text = (
                f"🚀 <b>Экспедиция завершена!</b>\n\n"
                f"Твой корабль вернулся из зоны.\n"
                f"💰 XGen: +{event.xgen_earned}\n"
                f"🧩 Фрагменты: +{event.fragments_earned}\n"
                f"📦 Предметов: {len(event.items_earned)}\n\n"
                f"Зайди в игру, чтобы забрать лут!"
            )
            await bot_service.send_message(event.telegram_id, text)
        except Exception as e:
            logger.exception(f"Error in expedition handler: {e}")

    return handler


def create_chapter_completed_handler(bot_service: TelegramBotService):
    async def handler(event: ChapterCompletedEvent) -> None:
        try:
            text = (
                f"📖 <b>Глава завершена!</b>\n\n"
                f"Поздравляем! Ты открыл все статьи в главе.\n"
                f"💰 Награда: {event.xgen_rewarded} XGen + {event.fragments_rewarded} фрагментов\n"
                f"🎁 Бонусный бокс уже в инвентаре!"
            )
            await bot_service.send_message(event.telegram_id, text)
        except Exception as e:
            logger.exception(f"Error in chapter handler: {e}")

    return handler


def create_daily_login_handler(bot_service: TelegramBotService):
    async def handler(event: DailyLoginCompletedEvent) -> None:
        try:
            if event.got_box:
                text = (
                    f"🎁 <b>Поздравляем!</b>\n\n"
                    f"Твой стрик: {event.new_streak} дней!\n"
                    f"Ты получил бонусный бокс за преданность.\n"
                    f"Зайди в игру, чтобы открыть его!"
                )
                await bot_service.send_message(event.telegram_id, text)
        except Exception as e:
            logger.exception(f"Error in daily login handler: {e}")

    return handler


def create_article_unlocked_handler(bot_service: TelegramBotService):
    async def handler(event: ArticleUnlockedEvent) -> None:
        pass

    return handler


def setup_event_handlers(bot_service: TelegramBotService) -> None:
    dispatcher.register(
        ExpeditionCompletedEvent,
        create_expedition_completed_handler(bot_service)
    )
    dispatcher.register(
        ChapterCompletedEvent,
        create_chapter_completed_handler(bot_service)
    )
    dispatcher.register(
        DailyLoginCompletedEvent,
        create_daily_login_handler(bot_service)
    )
    dispatcher.register(
        ArticleUnlockedEvent,
        create_article_unlocked_handler(bot_service)
    )
    logger.info("Event handlers registered successfully")
