"""Скрипт для сброса кэша всех конфигов в Redis.

Запуск:
    cd E:\CryptoProjects\exo-gen
    .venv\Scripts\python -m scripts.clear_config_cache
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.redis import invalidate_all_config_cache, test_connection


async def main():
    redis_ok = await test_connection()
    if not redis_ok:
        print("❌ Redis недоступен. Кэш не будет сброшен.")
        print("   Конфиги перезагрузятся автоматически при следующем запросе.")
        return

    deleted = await invalidate_all_config_cache()
    if deleted:
        print(f"✅ Кэш сброшен: удалено {deleted} ключей")
    else:
        print("ℹ️ Кэш пуст, ничего удалять не нужно")


if __name__ == "__main__":
    asyncio.run(main())
