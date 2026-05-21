"""Erosion and staking yield service — config-driven artifact lifecycle."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config_loader import load_config
from core.models import Artifact, Player

logger = logging.getLogger(__name__)


async def update_artifact_cycles(
    artifact_id: str,
    overdrive_mode: str,
    db: AsyncSession,
) -> dict:
    """Decrement artifact cycles after an expedition.

    Overdrive mode costs ×2 cycles.
    If cycles reach 0: status becomes "dormant", bonus drops to floor%.

    Returns:
        Dict with cycles_remaining, status, bonus_multiplier.
    """
    erosion_config = load_config("artifact_erosion")
    artifact = await db.get(Artifact, artifact_id)
    if not artifact:
        raise ValueError(f"Artifact not found: {artifact_id}")

    if artifact.status == "dormant":
        return {
            "cycles_remaining": 0,
            "status": "dormant",
            "bonus_multiplier": erosion_config["artifact_erosion"]["floor_percent"] / 100.0,
        }

    cycles_cost = 2 if overdrive_mode == "overdrive" else 1
    artifact.cycles_remaining -= cycles_cost

    floor_pct = erosion_config["artifact_erosion"]["floor_percent"]

    if artifact.cycles_remaining <= 0:
        artifact.cycles_remaining = 0
        artifact.status = "dormant"
        artifact.bonus_multiplier = floor_pct / 100.0
    else:
        artifact.bonus_multiplier = 1.0

    await db.flush()

    return {
        "cycles_remaining": artifact.cycles_remaining,
        "status": artifact.status,
        "bonus_multiplier": artifact.bonus_multiplier,
    }


async def calculate_staking_yield(
    player_id: str,
    artifact_id: str,
    db: AsyncSession,
) -> dict:
    """Calculate pending staking yield for an artifact.

    Checks: artifact active and staked, global pool remaining.
    Applies activity_multiplier based on player's weekly expeditions.
    Respects daily_cap_percent from config.

    Returns:
        Dict with pending_yield, daily_progress.
    """
    yield_config = load_config("artifact_erosion")["staking_yield"]
    artifact = await db.get(Artifact, artifact_id)
    if not artifact:
        raise ValueError(f"Artifact not found: {artifact_id}")

    if artifact.status != "active" or not artifact.staked_at:
        return {"pending_yield": 0.0, "daily_progress": 0.0}

    player = await db.get(Player, player_id)
    if not player:
        raise ValueError("Player not found")

    activity_level = _get_activity_level(player.weekly_expeditions)
    activity_multiplier = yield_config["activity_multiplier"].get(activity_level, 0.25)

    now = datetime.now(timezone.utc)
    last_claim = artifact.last_yield_claim or artifact.staked_at
    hours_elapsed = (now - last_claim).total_seconds() / 3600.0

    daily_cap = yield_config["global_pool_total"] * yield_config["daily_cap_percent"] / 100
    hourly_rate = daily_cap / 24.0 * activity_multiplier

    raw_yield = hours_elapsed * hourly_rate * artifact.bonus_multiplier
    daily_limit = daily_cap * activity_multiplier
    pending_yield = min(raw_yield, daily_limit)

    daily_progress = (pending_yield / daily_limit * 100) if daily_limit > 0 else 0.0

    return {
        "pending_yield": round(pending_yield, 4),
        "daily_progress": round(daily_progress, 2),
        "activity_level": activity_level,
        "bonus_multiplier": artifact.bonus_multiplier,
    }


async def calibrate_artifact(
    artifact_id: str,
    player_id: str,
    db: AsyncSession,
) -> dict:
    """Recalibrate an artifact: reset cycles, deduct cost.

    Cost: xgen + resource from config/artifact_erosion.json.

    Returns:
        Dict with artifact_id, cycles_remaining, status, costs.
    """
    erosion_config = load_config("artifact_erosion")
    calibration = erosion_config["artifact_erosion"]["calibration_cost"]

    artifact = await db.get(Artifact, artifact_id)
    if not artifact:
        raise ValueError(f"Artifact not found: {artifact_id}")
    if artifact.player_id != player_id:
        raise PermissionError("Artifact does not belong to player")

    player = await db.get(Player, player_id)
    if not player:
        raise ValueError("Player not found")
    if player.xgen_balance < calibration["xgen"]:
        raise ValueError(f"Insufficient $XGEN for calibration: need {calibration['xgen']}")

    player.xgen_balance -= calibration["xgen"]
    artifact.cycles_remaining = erosion_config["artifact_erosion"]["default_cycles"]
    artifact.status = "active"
    artifact.bonus_multiplier = 1.0

    from core.models import PlayerInventory
    result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player_id,
            PlayerInventory.slug == calibration["resource_slug"],
            PlayerInventory.quantity >= 1,
        )
    )
    resource_item = result.scalar_one_or_none()
    if resource_item:
        resource_item.quantity -= 1
    else:
        db.add(PlayerInventory(
            id=str(artifact_id),
            player_id=player_id,
            slug=calibration["resource_slug"],
            quantity=-1,
        ))

    await db.flush()

    return {
        "artifact_id": artifact_id,
        "cycles_remaining": artifact.cycles_remaining,
        "status": artifact.status,
        "xgen_cost": calibration["xgen"],
        "resource_cost_slug": calibration["resource_slug"],
    }


def _get_activity_level(weekly_expeditions: int) -> str:
    """Map weekly expedition count to activity level."""
    if weekly_expeditions >= 20:
        return "high"
    if weekly_expeditions >= 10:
        return "medium"
    if weekly_expeditions >= 3:
        return "low"
    return "idle"
