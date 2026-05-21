"""Ship service — repair, stability, and ship lifecycle management."""

import logging
import math
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config_loader import load_config
from core.models import PlayerInventory, Ship

logger = logging.getLogger(__name__)


async def repair_ship(
    player_id: str,
    ship_id: str,
    db: AsyncSession,
) -> dict:
    """Repair a ship using tier-matching repair materials.

    Calculates required mats based on current stability and repair_value.
    Deducts mats from inventory, restores stability to 100, clears repair status.

    Returns:
        Dict with new stability, mats_used, and ship status.

    Raises:
        ValueError: If ship not found, already at 100%, or insufficient mats.
    """
    ships_config = load_config("ships")
    repair_mats_config = load_config("repair_mats")

    # Get the ship
    ship = await db.get(Ship, ship_id)
    if not ship:
        raise ValueError("Ship not found")

    if ship.player_id != player_id:
        raise PermissionError("You don't own this ship")

    if ship.stability >= 100:
        raise ValueError("Ship is already at full stability")

    # Find matching repair mat by ship tier
    ship_entry = None
    for entry in ships_config.values():
        if entry.get("slug") == ship.slug:
            ship_entry = entry
            break

    if not ship_entry:
        raise ValueError(f"Ship config not found for slug: {ship.slug}")

    ship_tier = ship_entry.get("tier", 1)
    mat_slug = f"repair_matter_t{ship_tier}"

    mat_entry = repair_mats_config.get(mat_slug)
    if not mat_entry:
        raise ValueError(f"Repair mat not found for tier {ship_tier}")

    repair_value = mat_entry.get("repair_value", 5)
    damage = 100 - ship.stability
    required_mats = math.ceil(damage / repair_value)

    # Check inventory
    result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player_id,
            PlayerInventory.slug == mat_slug,
            PlayerInventory.quantity >= required_mats,
        )
    )
    inv_item = result.scalar_one_or_none()

    if not inv_item:
        # Check if player has any of this mat at all
        any_result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == player_id,
                PlayerInventory.slug == mat_slug,
            )
        )
        any_item = any_result.scalar_one_or_none()
        owned = any_item.quantity if any_item else 0
        raise ValueError(
            f"Недостаточно ремнаборов. Требуется: {required_mats}x {mat_entry['name']['ru']}, "
            f"есть: {owned}"
        )

    # Deduct mats
    inv_item.quantity -= required_mats

    # Repair ship
    ship.stability = 100
    ship.in_repair = False
    ship.repair_mode = None
    ship.repair_until = None

    await db.flush()

    logger.info(
        "Ship repaired: ship_id=%s tier=%d mats_used=%d",
        ship_id,
        ship_tier,
        required_mats,
    )

    return {
        "ship_id": ship_id,
        "stability": 100,
        "mats_used": required_mats,
        "mat_slug": mat_slug,
        "in_repair": False,
    }


async def get_ship_repair_info(
    player_id: str,
    ship_id: str,
    db: AsyncSession,
) -> dict:
    """Get repair info for a ship: current stability, required mats, owned mats."""
    repair_mats_config = load_config("repair_mats")
    ships_config = load_config("ships")

    ship = await db.get(Ship, ship_id)
    if not ship:
        raise ValueError("Ship not found")

    if ship.player_id != player_id:
        raise PermissionError("You don't own this ship")

    # Find ship tier
    ship_entry = None
    for entry in ships_config.values():
        if entry.get("slug") == ship.slug:
            ship_entry = entry
            break

    if not ship_entry:
        raise ValueError(f"Ship config not found for slug: {ship.slug}")

    ship_tier = ship_entry.get("tier", 1)
    mat_slug = f"repair_matter_t{ship_tier}"
    mat_entry = repair_mats_config.get(mat_slug, {})

    repair_value = mat_entry.get("repair_value", 5)
    damage = max(0, 100 - ship.stability)
    required_mats = math.ceil(damage / repair_value) if damage > 0 else 0

    # Check owned mats
    result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player_id,
            PlayerInventory.slug == mat_slug,
        )
    )
    inv_item = result.scalar_one_or_none()
    owned_mats = inv_item.quantity if inv_item else 0

    return {
        "ship_id": ship_id,
        "stability": ship.stability,
        "ship_tier": ship_tier,
        "mat_slug": mat_slug,
        "mat_name": mat_entry.get("name", {}).get("ru", ""),
        "repair_value": repair_value,
        "required_mats": required_mats,
        "owned_mats": owned_mats,
        "can_repair": owned_mats >= required_mats and ship.stability < 100,
    }
