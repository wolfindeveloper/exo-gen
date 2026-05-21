"""Player profile router."""

import logging

from fastapi import APIRouter, Depends

from api.middleware.auth import TelegramUser, get_current_player
from api.schemas.player import PlayerRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/player", tags=["player"])


@router.get("/me", response_model=PlayerRead)
async def get_player_me(
    user: TelegramUser = Depends(get_current_player),
) -> PlayerRead:
    """Return the current player's profile.

    MVP: returns mock data. Production will query PostgreSQL
    and hydrate the PlayerRead schema from the ORM model.
    """
    return PlayerRead(
        id=f"player_{user.telegram_id}",
        telegram_id=user.telegram_id,
        username=user.username,
        level=1,
        xp=0,
        tier=1,
        xgen_balance=0,
        verification_status="basic",
    )
