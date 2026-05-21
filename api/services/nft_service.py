"""NFT service — minting logic for T4-T5 ships and 1-of-1 artifacts.

Rules (from config/nft_minting.json):
- T1-T3 ships: off-chain (is_nft=false), stored in DB only
- T4-T5 ships: Fleet NFT (TEP-62), minted on TON
- Artifacts: 1-of-1 NFT, unique by SHA-256 recipe hash
- Pilot: SBT (Soul-Bound), non-transferable

This service bridges the game backend with blockchain operations.
All on-chain calls go through blockchain.ton_client.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from blockchain.ton_client import ton_client
from core.config_loader import load_config
from core.models import Artifact, Ship

logger = logging.getLogger(__name__)


async def mint_fleet_nft_if_eligible(
    ship_id: str,
    ship_slug: str,
    tier: int,
    owner_wallet_address: str,
    db: AsyncSession,
) -> dict | None:
    """Mint a Fleet NFT if the ship tier qualifies (T4+).

    T1-T3 ships remain off-chain. This function is a no-op for them.

    Args:
        ship_id: Database ship record ID.
        ship_slug: Ship slug for metadata.
        tier: Ship tier (1-5).
        owner_wallet_address: Player's connected TON wallet.
        db: Active database session.

    Returns:
        NFT metadata dict if minted, None if off-chain (T1-T3).
    """
    nft_config = load_config("nft_minting")["nft_minting"]["fleet_nft"]

    if tier < nft_config["min_tier"]:
        logger.info("Ship %s (tier %d) is off-chain, no NFT minting", ship_slug, tier)
        return None

    if not owner_wallet_address:
        logger.warning("Cannot mint NFT: no wallet connected for ship %s", ship_slug)
        return None

    nft_item = await ton_client.mint_fleet_nft(
        owner_address=owner_wallet_address,
        ship_slug=ship_slug,
        tier=tier,
    )

    ship = await db.get(Ship, ship_id)
    if ship:
        ship.is_nft = True

    logger.info(
        "Fleet NFT minted: ship=%s tier=%d index=%d collection=%s",
        ship_slug,
        tier,
        nft_item.item_index,
        nft_item.collection_address,
    )

    return {
        "nft_type": "fleet",
        "item_index": nft_item.item_index,
        "collection_address": nft_item.collection_address,
        "metadata_uri": nft_item.metadata_uri,
        "royalty_percent": nft_config["royalty_percent"],
        "standard": nft_config["standard"],
    }


async def mint_artifact_nft(
    artifact_id: str,
    artifact_slug: str,
    recipe_hash: str,
    owner_wallet_address: str,
    db: AsyncSession,
) -> dict:
    """Mint a 1-of-1 Artifact NFT.

    Each unique recipe hash produces exactly one NFT.
    The artifact must already exist in the database.

    Args:
        artifact_id: Database artifact record ID.
        artifact_slug: Artifact slug for metadata.
        recipe_hash: SHA-256 hash of the craft recipe.
        owner_wallet_address: Player's connected TON wallet.
        db: Active database session.

    Returns:
        NFT metadata dict.
    """
    if not owner_wallet_address:
        raise ValueError("Cannot mint artifact NFT: no wallet connected")

    nft_config = load_config("nft_minting")["nft_minting"]["artifact_nft"]

    nft_item = await ton_client.mint_artifact_nft(
        owner_address=owner_wallet_address,
        artifact_slug=artifact_slug,
        recipe_hash=recipe_hash,
    )

    artifact = await db.get(Artifact, artifact_id)
    if artifact:
        artifact.status = "minted"

    logger.info(
        "Artifact NFT minted: artifact=%s hash=%s index=%d",
        artifact_slug,
        recipe_hash[:8],
        nft_item.item_index,
    )

    return {
        "nft_type": "artifact",
        "item_index": nft_item.item_index,
        "collection_address": nft_item.collection_address,
        "metadata_uri": nft_item.metadata_uri,
        "royalty_percent": nft_config["royalty_percent"],
        "standard": nft_config["standard"],
        "unique_per_hash": nft_config["unique_per_hash"],
    }


async def mint_pilot_sbt(
    telegram_id: int,
    owner_wallet_address: str,
) -> dict:
    """Mint a Soul-Bound Pilot SBT for a verified player.

    SBTs are non-transferable and bound to the player's identity.

    Args:
        telegram_id: Player's Telegram user ID.
        owner_wallet_address: Player's connected TON wallet.

    Returns:
        SBT metadata dict.
    """
    if not owner_wallet_address:
        raise ValueError("Cannot mint Pilot SBT: no wallet connected")

    nft_config = load_config("nft_minting")["nft_minting"]["pilot_sbt"]

    sbt_item = await ton_client.mint_pilot_sbt(
        owner_address=owner_wallet_address,
        telegram_id=telegram_id,
    )

    logger.info(
        "Pilot SBT minted: telegram_id=%d index=%d soulbound=%s",
        telegram_id,
        sbt_item.item_index,
        sbt_item.is_soulbound,
    )

    return {
        "nft_type": "pilot_sbt",
        "item_index": sbt_item.item_index,
        "collection_address": sbt_item.collection_address,
        "metadata_uri": sbt_item.metadata_uri,
        "soulbound": nft_config["soulbound"],
        "transferable": nft_config["transferable"],
        "standard": nft_config["standard"],
    }


def is_nft_eligible(tier: int, entity_type: str = "fleet") -> bool:
    """Check if an entity qualifies for NFT minting.

    Args:
        tier: Entity tier (1-5).
        entity_type: "fleet" for ships, "artifact" for artifacts.

    Returns:
        True if NFT minting is applicable.
    """
    nft_config = load_config("nft_minting")["nft_minting"]

    if entity_type == "fleet":
        return tier >= nft_config["fleet_nft"]["min_tier"]
    if entity_type == "artifact":
        return nft_config["artifact_nft"]["unique_per_hash"]

    return False
