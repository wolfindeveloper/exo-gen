"""Config router: serves game balance JSON files from config/ with Redis caching."""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response, status

from core.redis import get_cached_config

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"

router = APIRouter(prefix="/config", tags=["config"])


def _load_config_sync(name: str) -> dict:
    """Синхронная загрузка конфига из файла (для передачи в get_cached_config)."""
    config_path = CONFIG_DIR / f"{name}.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"Config '{name}' not found")
    with open(config_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@router.get("/{name}")
async def get_config(name: str, response: Response) -> dict:
    """Load and return a game config JSON by name with Redis caching.

    The name must be a safe filename (alphanumeric + underscore/hyphen).
    Path traversal attempts are rejected with 404.

    Args:
        name: Config filename without extension (e.g. "fuels", "ships").
        response: FastAPI response object for setting cache headers.

    Returns:
        Parsed JSON config data.

    Raises:
        HTTPException: 404 if config file not found or name is unsafe.
    """
    if not name.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{name}' not found",
        )

    config_path = CONFIG_DIR / f"{name}.json"
    if not config_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{name}' not found",
        )

    # Проверяем, есть ли уже в кэше (для заголовка X-Cache)
    from core.redis import get_json, set_json
    from core.config import settings

    cache_key = f"config:{name}"
    cached = await get_json(cache_key)

    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached

    # Кэш-промах — загружаем и кэшируем
    try:
        data = _load_config_sync(name)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in config/%s.json: %s", name, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Config '{name}' contains invalid JSON",
        ) from exc
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{name}' not found",
        )

    await set_json(cache_key, data, ttl=settings.redis_cache_ttl)
    response.headers["X-Cache"] = "MISS"
    return data


@router.post("/{name}/invalidate")
async def invalidate_config(name: str) -> dict:
    """Сбросить кэш для указанного конфига.

    Полезно после обновления config/*.json файлов.
    """
    if not name.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{name}' not found",
        )

    from core.redis import get_redis_client, invalidate_config_cache

    try:
        await invalidate_config_cache(name)
        logger.info("Cache invalidated for config: %s", name)
        return {"status": "ok", "message": f"Cache cleared for '{name}'"}
    except Exception as exc:
        logger.warning("Failed to invalidate cache for '%s': %s", name, exc)
        return {"status": "warning", "message": f"Redis unavailable, config will reload on next request"}
