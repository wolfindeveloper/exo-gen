"""Expedition service — config-driven expedition lifecycle."""

import logging
import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config_loader import load_config
from core.models import Expedition, Player, PlayerInventory, Ship

logger = logging.getLogger(__name__)


async def start_expedition(
    player_id: str,
    ship_slug: str,
    tier: int,
    fuel_slug: str,
    overdrive_mode: str,
    db: AsyncSession,
) -> dict:
    """Start a new expedition for a player.

    Validates: player owns ship, has fuel, tier unlocked.
    Reads duration/loot/xp from config/expeditions.json.
    Randomizes duration within ±10%.

    Returns:
        Dict with expedition_id, estimated_end, tier, overdrive_mode.
    """
    expeditions_config = load_config("expeditions")
    ships_config = load_config("ships")

    expedition_entry = _find_expedition_by_tier(expeditions_config, tier)
    if not expedition_entry:
        raise ValueError(f"No expedition config for tier {tier}")

    if expedition_entry.get("requires_verification") == "VERIFIED":
        player = await db.get(Player, player_id)
        if not player or player.verification_status != "verified":
            raise PermissionError("Tier 5 expeditions require VERIFIED status")

    ship = await _get_player_ship(db, player_id, ship_slug)
    if not ship:
        raise ValueError(f"Player does not own ship: {ship_slug}")
    if ship.in_repair:
        raise ValueError("Ship is currently under repair")
    if ship.is_staked:
        raise ValueError("Staked ships cannot go on expeditions")

    has_fuel = await _has_inventory(db, player_id, fuel_slug, quantity=1)
    if not has_fuel:
        raise ValueError(f"Insufficient fuel: {fuel_slug}")

    hours = expedition_entry["duration_hours"]
    jitter = hours * 0.1
    randomized_hours = hours + random.uniform(-jitter, jitter)
    now = datetime.now(timezone.utc)
    estimated_end = now + timedelta(hours=randomized_hours)

    expedition = Expedition(
        id=str(uuid.uuid4()),
        player_id=player_id,
        ship_id=ship.id,
        slug=expedition_entry["slug"],
        tier=tier,
        overdrive_mode=overdrive_mode,
        status="pending",
        started_at=now,
        estimated_end=estimated_end,
        xp_reward=expedition_entry["xp_reward"],
    )
    db.add(expedition)

    await _consume_inventory(db, player_id, fuel_slug, quantity=1)

    ship.expedition_cycles += 1

    await db.flush()

    logger.info(
        "Expedition started: id=%s tier=%d mode=%s end=%s",
        expedition.id,
        tier,
        overdrive_mode,
        estimated_end.isoformat(),
    )

    return {
        "expedition_id": expedition.id,
        "estimated_end": estimated_end.isoformat(),
        "tier": tier,
        "overdrive_mode": overdrive_mode,
        "slug": expedition_entry["slug"],
    }


async def get_expedition(
    expedition_id: str,
    db: AsyncSession,
) -> Expedition | None:
    """Fetch a single expedition by ID."""
    result = await db.execute(select(Expedition).where(Expedition.id == expedition_id))
    return result.scalar_one_or_none()


async def get_active_expeditions(
    player_id: str,
    db: AsyncSession,
) -> list[Expedition]:
    """List all non-completed expeditions for a player."""
    result = await db.execute(
        select(Expedition)
        .where(Expedition.player_id == player_id)
        .where(Expedition.status.in_(["pending", "in_progress"]))
        .order_by(Expedition.started_at.desc())
    )
    return list(result.scalars().all())


def _find_expedition_by_tier(config: dict, tier: int) -> dict | None:
    """Find expedition config entry matching the given tier."""
    for entry in config.values():
        if entry.get("tier") == tier:
            return entry
    return None


async def _get_player_ship(
    db: AsyncSession,
    player_id: str,
    ship_slug: str,
) -> Ship | None:
    """Get a ship owned by the player with matching slug."""
    result = await db.execute(
        select(Ship).where(Ship.player_id == player_id, Ship.slug == ship_slug)
    )
    return result.scalar_one_or_none()


async def _has_inventory(
    db: AsyncSession,
    player_id: str,
    slug: str,
    quantity: int = 1,
) -> bool:
    """Check if player has enough of an inventory item."""
    result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player_id,
            PlayerInventory.slug == slug,
            PlayerInventory.quantity >= quantity,
        )
    )
    return result.scalar_one_or_none() is not None


async def _consume_inventory(
    db: AsyncSession,
    player_id: str,
    slug: str,
    quantity: int = 1,
) -> None:
    """Deduct inventory quantity. Creates negative record if not found (dev mode)."""
    result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player_id,
            PlayerInventory.slug == slug,
        )
    )
    item = result.scalar_one_or_none()
    if item:
        item.quantity -= quantity
    else:
        logger.warning("Inventory item %s not found for player %s, creating deficit", slug, player_id)
        db.add(PlayerInventory(
            id=str(uuid.uuid4()),
            player_id=player_id,
            slug=slug,
            quantity=-quantity,
        ))


async def _add_to_inventory(
    db: AsyncSession,
    player_id: str,
    slug: str,
    quantity: int = 1,
) -> None:
    """Add quantity to player inventory. Creates record if not found."""
    result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player_id,
            PlayerInventory.slug == slug,
        )
    )
    item = result.scalar_one_or_none()
    if item:
        item.quantity += quantity
    else:
        db.add(PlayerInventory(
            id=str(uuid.uuid4()),
            player_id=player_id,
            slug=slug,
            quantity=quantity,
        ))


def roll_repair_mat_drops(zone_config: dict) -> dict[str, int]:
    """Roll repair material drops based on zone's repair_drop_weights.

    Uses weighted random selection. Guarantees at least 1 repair mat drops.
    Higher-tier zones have higher chance for higher-tier mats.

    Args:
        zone_config: Zone config dict with repair_drop_weights.

    Returns:
        Dict mapping mat slug to quantity dropped.
    """
    weights = zone_config.get("repair_drop_weights")
    if not weights:
        return {}

    mat_slugs = list(weights.keys())
    mat_weights = list(weights.values())

    # Roll for repair mat drops — 1-3 mats per expedition
    num_drops = random.randint(1, 3)
    drops: dict[str, int] = {}

    for _ in range(num_drops):
        chosen = random.choices(mat_slugs, weights=mat_weights, k=1)[0]
        drops[chosen] = drops.get(chosen, 0) + 1

    return drops


async def apply_repair_mat_drops(
    db: AsyncSession,
    player_id: str,
    zone_config: dict,
) -> dict[str, int]:
    """Roll and apply repair mat drops to player inventory.

    Args:
        db: Database session.
        player_id: Player UUID.
        zone_config: Zone config with repair_drop_weights.

    Returns:
        Dict of mat slugs to quantities added.
    """
    drops = roll_repair_mat_drops(zone_config)

    for mat_slug, quantity in drops.items():
        await _add_to_inventory(db, player_id, mat_slug, quantity)

    if drops:
        logger.info(
            "Repair mats dropped for player %s: %s",
            player_id,
            ", ".join(f"{k}x{v}" for k, v in drops.items()),
        )

    return drops
