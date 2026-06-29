import json
import logging
from urllib.parse import parse_qs

from slowapi import Limiter
from slowapi.util import get_remote_address
from limits.storage import storage_from_string
from limits.storage.memory import MemoryStorage

from app.config.settings import settings

logger = logging.getLogger(__name__)


def get_telegram_or_ip_key(request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("tghash "):
        try:
            init_data = auth.replace("tghash ", "")
            parsed = parse_qs(init_data)
            data_dict = {k: v[0] for k, v in parsed.items()}
            user_json = data_dict.get("user", "{}")
            user = json.loads(user_json)
            if "id" in user:
                return str(user["id"])
        except Exception:
            logger.debug("Failed to parse init_data for rate limit key, falling back to IP")
    return get_remote_address(request)


try:
    storage = storage_from_string(settings.redis_url)
    logger.info("Rate limiter using Redis backend at %s", settings.redis_url)
except Exception:
    storage = MemoryStorage()
    logger.warning(
        "Redis unavailable for rate limiter, falling back to in-memory storage. "
        "Rate limits will reset on restart."
    )


limiter = Limiter(
    key_func=get_telegram_or_ip_key,
    storage_uri=settings.redis_url,
)
