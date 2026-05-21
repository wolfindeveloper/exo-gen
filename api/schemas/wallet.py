"""Pydantic schemas for wallet endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class WalletConnectRequest(BaseModel):
    """Request body for POST /wallet/connect."""

    address: str = Field(
        min_length=48,
        max_length=48,
        pattern="^[0-9a-fA-F]{48}$",
        description="TON wallet address (hex, 48 chars, no 0x prefix)",
    )
    network: str = Field(
        default="testnet",
        pattern="^(testnet|mainnet)$",
        description="TON network the wallet is connected to",
    )
    proof: dict | None = Field(
        default=None,
        description="TON Connect proof for address ownership verification",
    )


class WalletConnectResponse(BaseModel):
    """Response for successful wallet connection."""

    address: str
    network: str
    ton_balance: int = Field(description="Balance in nanotons")
    xgen_balance: int = Field(description="$XGEN jetton balance (smallest units)")
    connected: bool = True


class WalletBalanceResponse(BaseModel):
    """Response for GET /wallet/balance."""

    address: str
    ton_balance: int = Field(description="Balance in nanotons")
    xgen_balance: int = Field(description="$XGEN jetton balance (smallest units)")
    nft_count: int = Field(description="Number of NFTs owned", default=0)


class WalletDisconnectResponse(BaseModel):
    """Response for POST /wallet/disconnect."""

    address: str
    disconnected: bool = True
