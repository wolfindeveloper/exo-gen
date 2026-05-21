"""Dev data seeder — creates test player, ships, and inventory.

Использование:
    uv run python scripts/seed_dev_data.py

Идемпотентен: обновляет существующие записи до минимальных значений.
DEV ONLY — не использовать в продакшене.
"""

import asyncio
import json
import sys
import uuid
from pathlib import Path

# Фикс кодировки Windows-консоли для эмодзи
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import engine, async_session, init_db
from core.models import Player, Ship, PlayerInventory

# Пути к конфигам относительно корня проекта
CONFIG_DIR = Path(__file__).parent.parent / "config"


def _load_json(filename: str) -> dict:
    """Загружает JSON-файл из директории config/."""
    filepath = CONFIG_DIR / filename
    with open(filepath, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _get_first_t1_fuel() -> str:
    """Возвращает первый T1 fuel из config/fuels.json."""
    fuels = _load_json("fuels.json")
    for slug, data in fuels.items():
        if data.get("tier") == 1:
            return slug
    raise RuntimeError("Не найден T1 fuel в config/fuels.json")


async def _ensure_inventory(
    db: AsyncSession,
    player_id: str,
    slug: str,
    min_quantity: int,
) -> None:
    """Гарантирует минимальное количество предмета в инвентаре.

    Если записи нет — создаёт.
    Если количество меньше min_quantity — обновляет до min_quantity.
    """
    result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player_id,
            PlayerInventory.slug == slug,
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        # Записи нет — создаём
        item = PlayerInventory(
            id=str(uuid.uuid4()),
            player_id=player_id,
            slug=slug,
            quantity=min_quantity,
        )
        db.add(item)
        print(f"  ✅ Добавлено: {slug} ×{min_quantity}")
    elif item.quantity < min_quantity:
        # Запись есть, но количество меньше минимума — обновляем
        old_qty = item.quantity
        item.quantity = min_quantity
        print(f"  ✅ Обновлено: {slug} ×{old_qty} → ×{min_quantity}")
    else:
        # Количество достаточно
        print(f"  ⏭️  {slug} ×{item.quantity} (достаточно)")


async def seed() -> None:
    """Создаёт или обновляет тестовые данные для разработки."""
    print("🔧 Initializing dev database tables...")
    await init_db()

    async with async_session() as db:
        # --- Player ---
        player_id = "player_123"
        telegram_id = 123

        existing = await db.execute(select(Player).where(Player.id == player_id))
        player = existing.scalar_one_or_none()

        if player:
            print(f"✅ Player '{player.username}' already exists (id={player_id})")
        else:
            player = Player(
                id=player_id,
                telegram_id=telegram_id,
                username="Navigator",
                level=1,
                xp=0,
                tier=1,
                xgen_balance=1000,
                verification_status="basic",
                language="ru",
            )
            db.add(player)
            await db.flush()
            print(f"✅ Created player '{player.username}' with 1000 $XGEN")

        # --- Starter Ship ---
        ships_config = _load_json("ships.json")
        starter_slug = "seeker_dust_runner"

        if starter_slug not in ships_config:
            print(f"❌ Starter ship '{starter_slug}' not found in config/ships.json")
            return

        existing_ship = await db.execute(
            select(Ship).where(Ship.player_id == player_id, Ship.slug == starter_slug)
        )
        ship = existing_ship.scalar_one_or_none()

        if ship:
            print(f"✅ Ship '{starter_slug}' already owned by player")
        else:
            ship = Ship(
                id=str(uuid.uuid4()),
                player_id=player_id,
                slug=starter_slug,
                stability=100,
                is_nft=ships_config[starter_slug].get("is_nft", False),
                expedition_cycles=0,
            )
            db.add(ship)
            await db.flush()
            print(f"✅ Assigned starter ship '{starter_slug}' to player")

        # --- Starter Fuel (читаем из конфига) ---
        starter_fuel = _get_first_t1_fuel()
        fuel_qty = 50

        await _ensure_inventory(db, player_id, starter_fuel, fuel_qty)

        # --- Starter Essences ---
        for tier in range(1, 4):
            essence_slug = f"essence_t{tier}"
            await _ensure_inventory(db, player_id, essence_slug, 10)

        await db.commit()

        # --- Verification: читаем инвентарь из БД ---
        print("\n📋 Инвентарь player_123:")
        inv_result = await db.execute(
            select(PlayerInventory)
            .where(PlayerInventory.player_id == player_id)
            .order_by(PlayerInventory.slug)
        )
        items = inv_result.scalars().all()
        if items:
            for item in items:
                print(f"   {item.slug}: ×{item.quantity}")
        else:
            print("   (пусто)")

    print("\n🎉 Dev data seeding complete!")
    print(f"   Player: {player_id} (telegram_id={telegram_id})")
    print(f"   Ship:   {starter_slug}")
    print(f"   XGEN:   1000")
    print(f"   Fuel:   {fuel_qty}× {starter_fuel}")
    print(f"   Essences: 10× T1, 10× T2, 10× T3")


if __name__ == "__main__":
    asyncio.run(seed())
