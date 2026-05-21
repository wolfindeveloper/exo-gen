"""Authentication middleware dependencies."""

import json
import logging

from fastapi import Header, HTTPException, status

logger = logging.getLogger(__name__)


class TelegramUser:
    """Parsed Telegram user data from TMA headers."""

    def __init__(self, telegram_id: int, username: str) -> None:
        self.telegram_id = telegram_id
        self.username = username


async def get_current_player(
    x_telegram_user: str | None = Header(default=None, alias="X-Telegram-User"),
) -> TelegramUser:
    """Extract and validate Telegram user identity from request header.

    For MVP: parses the X-Telegram-User header containing JSON
    with Telegram user data. No JWT validation yet.

    Raises:
        HTTPException: 401 if header is missing or malformed.
    """
    if not x_telegram_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Telegram-User header",
        )

    try:
        data = json.loads(x_telegram_user)
        telegram_id = int(data.get("id", 0))
        username = str(data.get("username", ""))

        if telegram_id <= 0:
            raise ValueError("Invalid telegram_id")
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        logger.warning("Invalid X-Telegram-User header: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-Telegram-User header format",
        ) from exc

    return TelegramUser(telegram_id=telegram_id, username=username)
