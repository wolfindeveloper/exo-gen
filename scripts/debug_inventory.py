"""Debug one-liner: print player_123 inventory.

Использование:
    uv run python scripts/debug_inventory.py

Или как one-liner:
    uv run python -c "import asyncio; from scripts.debug_inventory import main; asyncio.run(main())"
"""

import asyncio
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from core.database import async_session
from core.models import PlayerInventory


async def main() -> None:
    """Выводит инвентарь player_123 из БД."""
    async with async_session() as db:
        result = await db.execute(
            select(PlayerInventory)
            .where(PlayerInventory.player_id == "player_123")
            .order_by(PlayerInventory.slug)
        )
        items = result.scalars().all()

        if items:
            print(f"📦 Инвентарь player_123 ({len(items)} предметов):")
            for item in items:
                status = "✅" if item.quantity > 0 else "❌"
                print(f"   {status} {item.slug}: ×{item.quantity}")
        else:
            print("⚠️  Инвентарь player_123 пуст")


if __name__ == "__main__":
    asyncio.run(main())
