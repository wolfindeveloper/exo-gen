import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qs

from fastapi import HTTPException

from app.config.settings import settings


@dataclass(frozen=True)
class TelegramUserDTO:
    telegram_id: int
    username: str
    first_name: str | None = None
    language_code: str | None = None


def verify_telegram_init_data(init_data: str, bot_token: str) -> TelegramUserDTO:
    """Verify Telegram initData HMAC-SHA256 signature per official docs.

    1. Parse init_data as query-string.
    2. Build data_check_string from sorted keys (excluding hash).
    3. Compute HMAC-SHA-256(HMAC-SHA-256(bot_token, "WebAppData"), data_check_string).
    4. Compare with hash using constant-time comparison.
    5. Verify auth_date is not older than 24 hours.
    """
    try:
        parsed_data = parse_qs(init_data)
        data_dict = {k: v[0] for k, v in parsed_data.items()}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid init data format")

    received_hash = data_dict.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash")

    auth_date_str = data_dict.get("auth_date")
    if auth_date_str is None:
        raise HTTPException(status_code=401, detail="Missing auth_date")
    try:
        auth_date = int(auth_date_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid auth_date format")

    now = int(time.time())
    if now - auth_date > settings.TELEGRAM_AUTH_MAX_AGE_SECONDS:
        raise HTTPException(
            status_code=401,
            detail="Auth data too old. Possible replay attack.",
        )

    sorted_items = sorted(data_dict.items())
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)

    secret_key = hmac.new(
        b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=401, detail="Invalid Telegram signature"
        )

    user_json = data_dict.get("user", "{}")
    try:
        user_data = json.loads(user_json)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user data in init data")

    telegram_id = user_data.get("id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="User ID not found in init data")

    return TelegramUserDTO(
        telegram_id=int(telegram_id),
        username=user_data.get("username", ""),
        first_name=user_data.get("first_name"),
        language_code=user_data.get("language_code"),
    )
