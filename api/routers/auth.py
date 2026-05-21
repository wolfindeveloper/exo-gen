"""Authentication router: Telegram and World ID login endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.middleware.auth import TelegramUser, get_current_player

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram")
async def auth_telegram(init_data: dict[str, Any]) -> dict[str, Any]:
    """Authenticate via Telegram Web App initData.

    MVP: mock validation. Production will verify HMAC-SHA256 signature
    against the bot token.

    Returns a mock JWT token and player stub.
    """
    try:
        user_data = init_data.get("user", {})
        telegram_id = user_data.get("id")
        username = user_data.get("username", f"user_{telegram_id}")

        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing user.id in initData",
            )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Telegram auth error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid initData payload",
        ) from exc

    return {
        "token": f"mock_jwt_{telegram_id}",
        "token_type": "Bearer",
        "player": {
            "telegram_id": telegram_id,
            "username": username,
            "verification_status": "basic",
        },
    }


@router.post("/worldid")
async def auth_worldid(
    action: str,
    signal: str,
    root_hash: str,
    nullifier_hash: str,
    proof: str,
) -> dict[str, Any]:
    """Authenticate via World ID (Worldcoin) verification.

    MVP: placeholder. Production will call the World ID verify endpoint
    and grant "verified" status with bonuses per spec section 11.
    """
    logger.info(
        "World ID auth attempt: nullifier=%s",
        nullifier_hash[:8] + "...",
    )

    return {
        "token": "mock_jwt_worldid",
        "token_type": "Bearer",
        "player": {
            "verification_status": "verified",
            "bonuses": {
                "xgen_multiplier": 1.2,
                "loot_multiplier": 1.15,
                "damage_reduction": 0.9,
            },
        },
    }


@router.get("/me")
async def auth_me(
    user: TelegramUser = Depends(get_current_player),
) -> dict[str, Any]:
    """Return authenticated player identity from Telegram header."""
    return {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "verification_status": "basic",
        "message": "Authenticated via Telegram header",
    }
