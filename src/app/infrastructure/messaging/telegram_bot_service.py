import logging

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    """Сервис для отправки сообщений через Telegram Bot API."""

    TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, bot_token: str | None = None):
        self.bot_token = bot_token or settings.BOT_TOKEN

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
    ) -> bool:
        """
        Отправляет сообщение пользователю.

        Args:
            chat_id: Telegram user ID
            text: Текст сообщения (поддерживает HTML разметку)
            parse_mode: "HTML" или "Markdown"

        Returns:
            True если сообщение отправлено, False в случае ошибки
        """
        url = self.TELEGRAM_API_URL.format(
            token=self.bot_token,
            method="sendMessage",
        )
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info(f"Message sent to chat_id={chat_id}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to send message to chat_id={chat_id}: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error sending message: {e}")
            return False
