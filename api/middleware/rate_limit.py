"""Middleware для rate limiting через sliding window algorithm."""

from __future__ import annotations

import time
import logging
from collections import defaultdict

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from core.redis import get_redis_client

logger = logging.getLogger(__name__)

# Локальный fallback если Redis недоступен
_local_windows: dict[str, list[float]] = defaultdict(list)


class RateLimitConfig:
    """Конфигурация rate limiting."""

    def __init__(
        self,
        requests_per_second: int = 10,
        burst_size: int = 20,
        window_seconds: int = 60,
        max_requests_per_window: int = 60,
    ):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.window_seconds = window_seconds
        self.max_requests_per_window = max_requests_per_window


# Конфигурация по умолчанию
default_config = RateLimitConfig()


async def rate_limit_middleware(request: Request, call_next) -> Response:
    """Middleware для ограничения частоты запросов.

    Использует sliding window algorithm с Redis для распределённого
    ограничения или локальный dict как fallback.

    Применяется к эндпоинтам:
    - /expeditions/start
    - /laboratory/craft
    - /auth/*

    Возвращает 429 с заголовком Retry-After при превышении лимита.
    """
    path = request.url.path

    # Проверяем, нужно ли применять rate limiting к этому пути
    if not _should_rate_limit(path):
        return await call_next(request)

    # Определяем клиентский идентификатор
    client_id = _get_client_id(request)

    # Пробуем Redis-based rate limiting
    try:
        redis_client = await get_redis_client()
        allowed = await _check_rate_limit_redis(
            redis_client, client_id, path
        )
    except Exception:
        # Fallback на локальный rate limiter
        allowed = _check_rate_limit_local(client_id, path)

    if not allowed:
        retry_after = default_config.window_seconds
        logger.warning(
            "Rate limit exceeded: client=%s path=%s",
            client_id,
            path,
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limit_exceeded",
                "detail": "Слишком много запросов. Попробуйте позже.",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    return await call_next(request)


def _should_rate_limit(path: str) -> bool:
    """Проверяет, нужно ли применять rate limiting к пути."""
    rate_limited_paths = [
        "/expeditions/start",
        "/laboratory/craft",
        "/auth/telegram",
        "/auth/worldid",
    ]
    return any(path.startswith(p) for p in rate_limited_paths)


def _get_client_id(request: Request) -> str:
    """Извлекает идентификатор клиента из запроса."""
    # Приоритет: X-Telegram-User > X-Forwarded-For > client.host
    telegram_user = request.headers.get("X-Telegram-User")
    if telegram_user:
        import json
        try:
            user_data = json.loads(telegram_user)
            return f"telegram:{user_data.get('id', 'unknown')}"
        except (json.JSONDecodeError, KeyError):
            pass

    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return f"ip:{forwarded_for.split(',')[0].strip()}"

    return f"ip:{request.client.host if request.client else 'unknown'}"


async def _check_rate_limit_redis(
    redis_client,
    client_id: str,
    path: str,
) -> bool:
    """Проверяет rate limit через Redis (sliding window)."""
    now = time.time()
    window_start = now - default_config.window_seconds

    key = f"rate_limit:{client_id}:{path}"

    # Удаляем старые записи за пределами окна
    await redis_client.zremrangebyscore(key, 0, window_start)

    # Считаем количество запросов в окне
    request_count = await redis_client.zcard(key)

    if request_count >= default_config.max_requests_per_window:
        return False

    # Добавляем текущий запрос
    await redis_client.zadd(key, {str(now): now})
    await redis_client.expire(key, default_config.window_seconds)

    return True


def _check_rate_limit_local(client_id: str, path: str) -> bool:
    """Локальный rate limiter (fallback)."""
    now = time.time()
    key = f"{client_id}:{path}"
    window_start = now - default_config.window_seconds

    # Удаляем старые записи
    _local_windows[key] = [
        ts for ts in _local_windows[key] if ts > window_start
    ]

    if len(_local_windows[key]) >= default_config.max_requests_per_window:
        return False

    _local_windows[key].append(now)
    return True
