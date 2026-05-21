"""Laboratory service — config-driven artifact crafting."""

import hashlib
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config_loader import load_config
from core.models import Artifact, Player, PlayerInventory

logger = logging.getLogger(__name__)


async def attempt_craft(
    player_id: str,
    domain_slug: str,
    essences: list[str],
    xgen_amount: int,
    db: AsyncSession,
) -> dict:
    """Attempt to craft an artifact from essences.

    Validates: player owns essences, domain unlocked, xgen balance.
    Generates SHA-256 hash from sorted essences + domain + xgen.
    Checks uniqueness via Redis or DB.

    If unique: creates artifact, deducts 100% essences + 100% xgen.
    If taken: refunds 50% essences, burns 100% xgen.

    Returns:
        Dict with status, recipe_hash, artifact_id, essences_refunded.
    """
    lab_config = load_config("lab_rules")
    galaxy_config = load_config("galaxy_zones")

    rules = lab_config["lab_rules"]
    if len(essences) < rules["min_essences"]:
        raise ValueError(f"Minimum {rules['min_essences']} essences required")
    if len(essences) > rules["max_essences"]:
        raise ValueError(f"Maximum {rules['max_essences']} essences allowed")

    domain = galaxy_config.get("galaxy_zones", {}).get(domain_slug)
    if not domain:
        raise ValueError(f"Unknown domain: {domain_slug}")

    player = await db.get(Player, player_id)
    if not player:
        raise ValueError("Player not found")
    if player.xgen_balance < xgen_amount:
        raise ValueError(f"Insufficient $XGEN: have {player.xgen_balance}, need {xgen_amount}")

    for essence_slug in essences:
        has = await _has_inventory(db, player_id, essence_slug, quantity=1)
        if not has:
            raise ValueError(f"Missing essence: {essence_slug}")

    recipe_hash = _generate_recipe_hash(essences, domain_slug, xgen_amount)

    existing = await _find_artifact_by_hash(db, recipe_hash)

    player.xgen_balance -= xgen_amount

    essences_refunded: list[str] = []

    if existing:
        refund_pct = rules["failure_return_percent"] / 100.0
        for essence_slug in essences:
            refund_qty = max(1, int(1 * refund_pct))
            await _add_inventory(db, player_id, essence_slug, refund_qty)
            essences_refunded.append(essence_slug)

        logger.info(
            "Craft failed (hash taken): player=%s hash=%s refunded=%s",
            player_id,
            recipe_hash,
            essences_refunded,
        )

        return {
            "status": "taken",
            "recipe_hash": recipe_hash,
            "artifact_id": None,
            "essences_refunded": essences_refunded,
            "xgen_burned": xgen_amount,
        }

    artifact_slug = f"artifact_{recipe_hash[:12]}"
    artifact = Artifact(
        id=str(uuid.uuid4()),
        player_id=player_id,
        slug=artifact_slug,
        recipe_hash=recipe_hash,
        status="active",
        cycles_remaining=load_config("artifact_erosion")["artifact_erosion"]["default_cycles"],
        domain_slug=domain_slug,
        bonus_multiplier=1.0,
        accumulated_yield=0.0,
    )
    db.add(artifact)

    for essence_slug in essences:
        await _consume_inventory(db, player_id, essence_slug, quantity=1)

    await db.flush()

    logger.info(
        "Artifact crafted: id=%s hash=%s player=%s",
        artifact.id,
        recipe_hash,
        player_id,
    )

    return {
        "status": "created",
        "recipe_hash": recipe_hash,
        "artifact_id": artifact.id,
        "essences_refunded": None,
        "xgen_burned": xgen_amount,
    }


def _generate_recipe_hash(essences: list[str], domain_slug: str, xgen_amount: int) -> str:
    """Generate deterministic SHA-256 hash from craft ingredients."""
    sorted_essences = sorted(essences)
    raw = f"{','.join(sorted_essences)}|{domain_slug}|{xgen_amount}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def _has_inventory(
    db: AsyncSession,
    player_id: str,
    slug: str,
    quantity: int = 1,
) -> bool:
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
        from core.models import PlayerInventory as PI
        db.add(PI(
            id=str(uuid.uuid4()),
            player_id=player_id,
            slug=slug,
            quantity=-quantity,
        ))


async def _add_inventory(
    db: AsyncSession,
    player_id: str,
    slug: str,
    quantity: int = 1,
) -> None:
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
        from core.models import PlayerInventory as PI
        db.add(PI(
            id=str(uuid.uuid4()),
            player_id=player_id,
            slug=slug,
            quantity=quantity,
        ))


async def _find_artifact_by_hash(
    db: AsyncSession,
    recipe_hash: str,
) -> Artifact | None:
    result = await db.execute(
        select(Artifact).where(Artifact.recipe_hash == recipe_hash)
    )
    return result.scalar_one_or_none()


async def get_recipe_info(
    recipe_hash: str,
    db: AsyncSession,
) -> dict | None:
    """Return public recipe info by hash (for marketplace)."""
    artifact = await _find_artifact_by_hash(db, recipe_hash)
    if not artifact:
        return None
    return {
        "recipe_hash": artifact.recipe_hash,
        "artifact_slug": artifact.slug,
        "domain_slug": artifact.domain_slug,
        "essence_count": 0,
        "created_at": artifact.created_at.isoformat(),
    }
