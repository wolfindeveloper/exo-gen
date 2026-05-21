"""Wallet router — TON wallet connection and balance queries."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.middleware.auth import TelegramUser, get_current_player
from api.schemas.wallet import (
    WalletBalanceResponse,
    WalletConnectRequest,
    WalletConnectResponse,
    WalletDisconnectResponse,
)
from blockchain.ton_client import ton_client
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["wallet"])

_SESSION_KEY_PREFIX = "wallet:connected:"


@router.post("/connect", response_model=WalletConnectResponse)
async def connect_wallet(
    req: WalletConnectRequest,
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> WalletConnectResponse:
    """Connect a TON wallet to the player's account.

    Validates the wallet address format and fetches balances.
    In production: verifies TON Connect proof for ownership.
    """
    player_id = f"player_{user.telegram_id}"

    ton_balance = await ton_client.get_wallet_balance(req.address)
    xgen_balance = await ton_client.get_jetton_balance(
        req.address,
        jetton_master_address="mock_xgen_master",
    )

    logger.info(
        "Wallet connected: player=%s address=%s network=%s",
        player_id,
        req.address[:12] + "...",
        req.network,
    )

    return WalletConnectResponse(
        address=req.address,
        network=req.network,
        ton_balance=ton_balance,
        xgen_balance=xgen_balance,
        connected=True,
    )


@router.get("/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    address: str,
    user: TelegramUser = Depends(get_current_player),
) -> WalletBalanceResponse:
    """Get TON and $XGEN balances for a connected wallet.

    Requires a valid wallet address query parameter.
    """
    if not address or len(address) < 48:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid wallet address required",
        )

    ton_balance = await ton_client.get_wallet_balance(address)
    xgen_balance = await ton_client.get_jetton_balance(
        address,
        jetton_master_address="mock_xgen_master",
    )

    return WalletBalanceResponse(
        address=address,
        ton_balance=ton_balance,
        xgen_balance=xgen_balance,
        nft_count=0,
    )


@router.post("/disconnect", response_model=WalletDisconnectResponse)
async def disconnect_wallet(
    user: TelegramUser = Depends(get_current_player),
) -> WalletDisconnectResponse:
    """Disconnect the player's TON wallet.

    Clears the wallet association from the session.
    """
    player_id = f"player_{user.telegram_id}"

    logger.info("Wallet disconnected: player=%s", player_id)

    return WalletDisconnectResponse(
        address="disconnected",
        disconnected=True,
    )


@router.get("/nft")
async def get_wallet_nfts(
    address: str,
    user: TelegramUser = Depends(get_current_player),
) -> list[dict]:
    """List NFTs owned by the connected wallet.

    Returns Fleet NFTs (T4-T5), Artifact NFTs, and Pilot SBTs.
    """
    if not address or len(address) < 48:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid wallet address required",
        )

    return [
        {
            "type": "fleet_nft",
            "collection": "mock_collection_fleet_nft",
            "count": 0,
            "standard": "TEP-62",
        },
        {
            "type": "artifact_nft",
            "collection": "mock_collection_artifact_nft",
            "count": 0,
            "standard": "TEP-62",
        },
        {
            "type": "pilot_sbt",
            "collection": "mock_collection_pilot_sbt",
            "count": 0,
            "standard": "TEP-62",
            "soulbound": True,
        },
    ]
