"""TON blockchain client wrapper.

Provides async interface for TON network operations:
- Wallet management
- Jetton transfers ($XGEN)
- NFT minting and transfers
- Transaction verification

For local development: all calls are mocked with realistic responses.
Production will use tonutils/pytoniq for real TON RPC calls.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.config import settings
from core.config_loader import load_config

logger = logging.getLogger(__name__)


@dataclass
class TonTransaction:
    """Represents a TON blockchain transaction."""

    tx_hash: str
    from_address: str
    to_address: str
    amount: int
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class NftItem:
    """Represents an NFT item on TON (TEP-62)."""

    item_index: int
    owner_address: str
    collection_address: str
    metadata_uri: str
    is_soulbound: bool = False


class TonClient:
    """Async TON client for testnet/mainnet operations.

    In dev mode (testnet with no API key), all methods return
    mock data that simulates real blockchain responses.
    """

    def __init__(self) -> None:
        self.network = settings.ton_network
        self.api_key = settings.ton_api_key
        self.is_dev = self.network == "testnet" and not self.api_key
        self._pending_tx: dict[str, TonTransaction] = {}

    async def get_wallet_balance(self, address: str) -> int:
        """Get TON balance for a wallet address (nanotons).

        Returns mock balance in dev mode.
        """
        if self.is_dev:
            logger.info("[MOCK] get_wallet_balance: %s -> 5.0 TON", address)
            return 5_000_000_000

        raise NotImplementedError("Production TON RPC not yet implemented")

    async def get_jetton_balance(
        self,
        wallet_address: str,
        jetton_master_address: str,
    ) -> int:
        """Get $XGEN jetton balance for a wallet.

        Returns mock balance in dev mode.
        """
        if self.is_dev:
            balance = 10_000 * (10**9)
            logger.info("[MOCK] get_jetton_balance: %s -> %d XGEN", wallet_address, balance)
            return balance

        raise NotImplementedError("Production TON RPC not yet implemented")

    async def send_ton(
        self,
        from_address: str,
        to_address: str,
        amount_nanotons: int,
    ) -> TonTransaction:
        """Send TON coins between wallets.

        Returns mock transaction in dev mode.
        """
        tx = TonTransaction(
            tx_hash=f"mock_tx_{uuid.uuid4().hex[:16]}",
            from_address=from_address,
            to_address=to_address,
            amount=amount_nanotons,
            status="confirmed" if self.is_dev else "pending",
        )
        self._pending_tx[tx.tx_hash] = tx
        logger.info(
            "[MOCK] send_ton: %s -> %s (%d nanotons) tx=%s",
            from_address,
            to_address,
            amount_nanotons,
            tx.tx_hash,
        )
        return tx

    async def mint_fleet_nft(
        self,
        owner_address: str,
        ship_slug: str,
        tier: int,
    ) -> NftItem:
        """Mint a Fleet NFT (T4-T5 ships only).

        Validates tier >= 4 via config/nft_minting.json.
        Returns mock NFT item in dev mode.
        """
        nft_config = load_config("nft_minting")["nft_minting"]["fleet_nft"]
        if tier < nft_config["min_tier"]:
            raise ValueError(
                f"Fleet NFT minting requires tier >= {nft_config['min_tier']}, got {tier}"
            )

        if self.is_dev:
            item = NftItem(
                item_index=hash(ship_slug) % 1000000,
                owner_address=owner_address,
                collection_address="mock_collection_fleet_nft",
                metadata_uri=f"mock://nft/fleet/{ship_slug}",
                is_soulbound=False,
            )
            logger.info(
                "[MOCK] mint_fleet_nft: ship=%s tier=%d owner=%s index=%d",
                ship_slug,
                tier,
                owner_address,
                item.item_index,
            )
            return item

        raise NotImplementedError("Production NFT minting not yet implemented")

    async def mint_artifact_nft(
        self,
        owner_address: str,
        artifact_slug: str,
        recipe_hash: str,
    ) -> NftItem:
        """Mint a 1-of-1 Artifact NFT.

        Each unique recipe_hash produces exactly one NFT.
        Returns mock NFT item in dev mode.
        """
        if self.is_dev:
            item = NftItem(
                item_index=hash(recipe_hash) % 1000000,
                owner_address=owner_address,
                collection_address="mock_collection_artifact_nft",
                metadata_uri=f"mock://nft/artifact/{artifact_slug}",
                is_soulbound=False,
            )
            logger.info(
                "[MOCK] mint_artifact_nft: artifact=%s hash=%s owner=%s",
                artifact_slug,
                recipe_hash[:8],
                owner_address,
            )
            return item

        raise NotImplementedError("Production artifact minting not yet implemented")

    async def mint_pilot_sbt(
        self,
        owner_address: str,
        telegram_id: int,
    ) -> NftItem:
        """Mint a Soul-Bound Pilot SBT (non-transferable).

        One SBT per player, bound to their identity.
        Returns mock SBT in dev mode.
        """
        if self.is_dev:
            item = NftItem(
                item_index=telegram_id % 1000000,
                owner_address=owner_address,
                collection_address="mock_collection_pilot_sbt",
                metadata_uri=f"mock://sbt/pilot/{telegram_id}",
                is_soulbound=True,
            )
            logger.info(
                "[MOCK] mint_pilot_sbt: telegram_id=%d owner=%s",
                telegram_id,
                owner_address,
            )
            return item

        raise NotImplementedError("Production SBT minting not yet implemented")

    async def verify_transaction(self, tx_hash: str) -> bool:
        """Verify a transaction is confirmed on-chain.

        Returns True for mock transactions in dev mode.
        """
        if self.is_dev:
            return True

        tx = self._pending_tx.get(tx_hash)
        if tx:
            return tx.status == "confirmed"

        raise NotImplementedError("Production tx verification not yet implemented")

    async def get_nft_owner(self, collection_address: str, item_index: int) -> str | None:
        """Get the owner address of a specific NFT item.

        Returns mock owner in dev mode.
        """
        if self.is_dev:
            return "mock_owner_address"

        raise NotImplementedError("Production NFT owner lookup not yet implemented")


ton_client = TonClient()
