"""Async Redis client and helper utilities."""

import json
import logging
from collections.abc import AsyncGenerator, Callable
from typing import Any

import redis.asyncio as aioredis

from core.config import settings

logger = logging.getLogger(__name__)

redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """Return the singleton async Redis client, creating it if needed."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            health_check_interval=10,
        )
    return redis_client


async def get_redis() -> AsyncGenerator[aioredis.Redis, Any]:
    """FastAPI dependency yielding an async Redis connection."""
    client = await get_redis_client()
    yield client


async def set_json(key: str, data: Any, ttl: int | None = None) -> bool:
    """Serialize and store a Python object as JSON in Redis."""
    client = await get_redis_client()
    serialized = json.dumps(data, ensure_ascii=False)
    if ttl:
        await client.setex(key, ttl, serialized)
    else:
        await client.set(key, serialized)
    return True


async def get_json(key: str) -> Any | None:
    """Retrieve and deserialize a JSON object from Redis."""
    client = await get_redis_client()
    raw = await client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def get_cached_config(
    key: str,
    loader: Callable[[], Any],
    ttl: int | None = None,
) -> Any:
    """Получает конфиг из Redis-кэша или загружает через loader.

    Args:
        key: Ключ для Redis (например, "config:ships").
        loader: Асинхронная или синхронная функция загрузки конфига.
        ttl: Время жизни в секундах. По умолчанию берётся из settings.redis_cache_ttl.

    Returns:
        Загруженный конфиг (dict или list).
    """
    effective_ttl = ttl or settings.redis_cache_ttl
    cache_key = f"config:{key}"

    # Пробуем получить из кэша
    cached = await get_json(cache_key)
    if cached is not None:
        logger.debug("Config cache HIT: %s", key)
        return cached

    # Кэш промах — загружаем через loader
    logger.debug("Config cache MISS: %s, loading...", key)
    import inspect
    result = loader()
    if inspect.iscoroutine(result):
        result = await result

    # Сохраняем в кэш с TTL
    await set_json(cache_key, result, ttl=effective_ttl)
    return result


async def invalidate_config_cache(key: str) -> bool:
    """Инвалидирует кэш конкретного конфига.

    Args:
        key: Ключ конфига (например, "ships").

    Returns:
        True если ключ был удалён, False если его не было.
    """
    client = await get_redis_client()
    cache_key = f"config:{key}"
    deleted = await client.delete(cache_key)
    if deleted:
        logger.info("Config cache invalidated: %s", key)
    return bool(deleted)


async def invalidate_all_config_cache() -> int:
    """Инвалидирует весь кэш конфигов.

    Returns:
        Количество удалённых ключей.
    """
    client = await get_redis_client()
    keys = await client.keys("config:*")
    if keys:
        deleted = await client.delete(*keys)
        logger.info("All config cache invalidated (%d keys)", deleted)
        return deleted
    return 0


async def test_connection() -> bool:
    """Verify Redis connectivity with a PING command."""
    try:
        client = await get_redis_client()
        return await client.ping()
    except Exception:
        return False


async def close_redis() -> None:
    """Close the Redis connection pool on shutdown."""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
