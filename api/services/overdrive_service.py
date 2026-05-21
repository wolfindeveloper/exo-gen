"""Overdrive service — config-driven risk/reward calculations."""

import logging
import random

from core.config_loader import load_config

logger = logging.getLogger(__name__)


def calculate_overdrive_result(
    mode: str,
    base_loot: dict[str, int],
    ship_stability: int,
    xp_base: int,
) -> dict:
    """Calculate the result of an expedition with overdrive modifiers.

    Reads multipliers and damage chances from config/overdrive.json.
    Applies loot multiplier, time reduction, and damage roll.

    Args:
        mode: "stable", "push", or "overdrive".
        base_loot: Dict of {slug: quantity} from expedition loot table.
        ship_stability: Current ship stability (0-100).
        xp_base: Base XP reward for the expedition.

    Returns:
        Dict with final_loot, damage_occurred, new_stability, xp_reward.
    """
    overdrive_config = load_config("overdrive")
    mode_config = overdrive_config.get(mode)
    if not mode_config:
        raise ValueError(f"Unknown overdrive mode: {mode}")

    loot_multiplier = mode_config["loot_multiplier"]
    final_loot = {
        slug: max(1, int(qty * loot_multiplier))
        for slug, qty in base_loot.items()
    }

    base_damage_pct = mode_config["damage_chance_percent"]
    stability_reduction = (ship_stability // 10) * 5
    effective_damage_pct = max(0, base_damage_pct - stability_reduction)

    damage_occurred = random.randint(1, 100) <= effective_damage_pct

    new_stability = ship_stability
    if damage_occurred:
        damage_amount = random.randint(5, 20)
        new_stability = max(0, ship_stability - damage_amount)

    xp_reward = int(xp_base * loot_multiplier)

    return {
        "final_loot": final_loot,
        "damage_occurred": damage_occurred,
        "new_stability": new_stability,
        "xp_reward": xp_reward,
        "loot_multiplier": loot_multiplier,
    }


def roll_essence_drop(
    mode: str,
    essence_tier: int,
    daily_essence_count: int,
    max_per_day: int,
) -> tuple[bool, str]:
    """Determine if an essence drops based on mode and anti-farm limits.

    Args:
        mode: Overdrive mode affecting drop chance.
        essence_tier: Tier of the essence (1-5).
        daily_essence_count: Number of essences already farmed today.
        max_per_day: Maximum essences allowed per day from config.

    Returns:
        Tuple of (dropped: bool, essence_slug: str | "").
    """
    if daily_essence_count >= max_per_day:
        return False, ""

    essence_config = load_config("essence_drop")
    mode_data = essence_config["essence_drop"].get(mode)
    if not mode_data:
        return False, ""

    if essence_tier >= 4 and not mode_data.get("t4_unlocked", False):
        return False, ""
    if essence_tier >= 5 and not mode_data.get("t5_unlocked", False):
        return False, ""

    base_chance = mode_data["base_chance_percent"]
    multiplier = mode_data.get("multiplier", 1.0)
    effective_chance = min(100, base_chance * multiplier)

    if random.randint(1, 100) <= effective_chance:
        return True, f"essence_t{essence_tier}"

    return False, ""
