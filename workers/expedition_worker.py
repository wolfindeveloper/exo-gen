"""Expedition completion Celery task."""

import logging
import random
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from core.config_loader import load_config
from core.database import async_session
from core.models import Expedition, Player, PlayerInventory, Ship
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="workers.expedition_worker.complete_expedition")
def complete_expedition(self, expedition_id: str) -> dict:
    """Complete an expedition: generate loot, award XP, apply overdrive.

    This is a Celery task that runs when an expedition timer expires.
    Uses synchronous SQLAlchemy since Celery workers don't use async.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from core.config import settings

    engine = create_engine(settings.database_url_sync)

    with Session(engine) as db:
        expedition = db.get(Expedition, expedition_id)
        if not expedition:
            logger.error("Expedition not found: %s", expedition_id)
            return {"status": "error", "reason": "not_found"}

        if expedition.status == "completed":
            logger.warning("Expedition already completed: %s", expedition_id)
            return {"status": "skipped", "reason": "already_completed"}

        expedition.status = "completed"
        expedition.completed_at = datetime.now(timezone.utc)

        expeditions_config = load_config("expeditions")
        loot_table = _find_expedition_loot(expeditions_config, expedition.tier)
        if not loot_table:
            logger.error("No loot table for tier %d", expedition.tier)
            return {"status": "error", "reason": "no_loot_table"}

        base_loot = _generate_base_loot(loot_table)

        try:
            from api.services.overdrive_service import calculate_overdrive_result, roll_essence_drop

            ship = db.get(Ship, expedition.ship_id)
            ship_stability = ship.stability if ship else 100

            overdrive_result = calculate_overdrive_result(
                mode=expedition.overdrive_mode,
                base_loot=base_loot,
                ship_stability=ship_stability,
                xp_base=expedition.xp_reward,
            )

            expedition.loot = overdrive_result["final_loot"]
            expedition.xp_reward = overdrive_result["xp_reward"]
            expedition.damage_occurred = overdrive_result["damage_occurred"]

            if ship:
                ship.stability = overdrive_result["new_stability"]

            essence_config = load_config("essence_drop")
            max_per_day = essence_config["essence_drop"]["anti_farm"]["max_essences_per_day"]
            daily_key = f"essence:daily:{expedition.player_id}"

            essence_dropped, essence_slug = roll_essence_drop(
                mode=expedition.overdrive_mode,
                essence_tier=expedition.tier,
                daily_essence_count=0,
                max_per_day=max_per_day,
            )

            if essence_dropped and essence_slug:
                _add_inventory_sync(db, expedition.player_id, essence_slug, 1)

            player = db.get(Player, expedition.player_id)
            if player:
                player.xp += expedition.xp_reward
                player.level = _calculate_level(player.xp)
                player.weekly_expeditions += 1

            # Roll repair mat drops based on zone tier
            zones_config = load_config("galaxy_zones")
            zone_config = _find_zone_by_tier(zones_config, expedition.tier)
            repair_drops = {}
            if zone_config:
                repair_drops = _roll_repair_mat_drops_sync(zone_config)
                for mat_slug, quantity in repair_drops.items():
                    _add_inventory_sync(db, expedition.player_id, mat_slug, quantity)

            db.commit()

            logger.info(
                "Expedition completed: id=%s loot=%s xp=%d damage=%s repair_mats=%s",
                expedition_id,
                overdrive_result["final_loot"],
                expedition.xp_reward,
                overdrive_result["damage_occurred"],
                repair_drops,
            )

            return {
                "status": "completed",
                "loot": overdrive_result["final_loot"],
                "xp_reward": expedition.xp_reward,
                "damage_occurred": overdrive_result["damage_occurred"],
            }

        except Exception as exc:
            db.rollback()
            logger.error("Expedition completion failed: %s", exc)
            return {"status": "error", "reason": str(exc)}


def _find_expedition_loot(config: dict, tier: int) -> list[str] | None:
    for entry in config.values():
        if entry.get("tier") == tier:
            return entry.get("loot_table", [])
    return None


def _find_zone_by_tier(config: dict, tier: int) -> dict | None:
    """Find zone config by tier from galaxy_zones."""
    zones = config.get("galaxy_zones", config)
    for entry in zones.values():
        if entry.get("tier") == tier:
            return entry
    return None


def _roll_repair_mat_drops_sync(zone_config: dict) -> dict[str, int]:
    """Roll repair material drops based on zone's repair_drop_weights (sync version)."""
    weights = zone_config.get("repair_drop_weights")
    if not weights:
        return {}

    mat_slugs = list(weights.keys())
    mat_weights = list(weights.values())

    num_drops = random.randint(1, 3)
    drops: dict[str, int] = {}

    for _ in range(num_drops):
        chosen = random.choices(mat_slugs, weights=mat_weights, k=1)[0]
        drops[chosen] = drops.get(chosen, 0) + 1

    return drops


def _generate_base_loot(loot_table: list[str]) -> dict[str, int]:
    return {slug: random.randint(1, 5) for slug in loot_table}


def _add_inventory_sync(db: Session, player_id: str, slug: str, quantity: int) -> None:
    result = db.execute(
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


def _calculate_level(xp: int) -> int:
    """Calculate level from XP using formula: XP_req = floor(100 * level^1.8)."""
    import math
    level = 1
    while level < 100:
        required = math.floor(100 * (level + 1) ** 1.8)
        if xp < required:
            break
        level += 1
    return level
