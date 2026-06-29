import logging

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    """Сервис для отправки сообщений через Telegram Bot API."""

    TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, bot_token: str | None = None):
        self.bot_token = bot_token or settings.BOT_TOKEN

    async def _call_api(
        self, method: str, payload: dict, timeout: float = 10.0
    ) -> dict | None:
        url = self.TELEGRAM_API_URL.format(
            token=self.bot_token,
            method=method,
        )
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                if not data.get("ok"):
                    logger.error(f"Telegram API error for {method}: {data}")
                    return None
                return data.get("result")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Telegram {method}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error calling Telegram {method}: {e}")
            return None

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
    ) -> bool:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        result = await self._call_api("sendMessage", payload)
        if result:
            logger.info(f"Message sent to chat_id={chat_id}")
            return True
        return False

    async def create_invoice_link(
        self,
        title: str,
        description: str,
        prices: list[dict],
        payload: str,
    ) -> str | None:
        api_payload = {
            "title": title,
            "description": description,
            "payload": payload,
            "currency": "XTR",
            "prices": prices,
        }
        result = await self._call_api("createInvoiceLink", api_payload, timeout=15.0)
        if result:
            logger.info(f"Invoice link created: {result}")
            return result
        return None

    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool = True,
        error_message: str | None = None,
    ) -> bool:
        payload: dict = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok,
        }
        if not ok and error_message:
            payload["error_message"] = error_message
        result = await self._call_api("answerPreCheckoutQuery", payload)
        return result is not None

    async def set_webhook(self, webhook_url: str) -> bool:
        payload = {
            "url": webhook_url,
            "allowed_updates": ["pre_checkout_query", "successful_payment"],
        }
        result = await self._call_api("setWebhook", payload)
        return result is not None
