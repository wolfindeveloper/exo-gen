"""Expedition router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.middleware.auth import TelegramUser, get_current_player
from api.schemas.expedition import ActiveExpeditionRead, ExpeditionRead, ExpeditionStartRequest
from api.services import expedition_service
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expeditions", tags=["expeditions"])


@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_expedition(
    req: ExpeditionStartRequest,
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Launch a new expedition.

    Validates ship ownership, fuel availability, and tier access.
    """
    player_id = f"player_{user.telegram_id}"

    try:
        result = await expedition_service.start_expedition(
            player_id=player_id,
            ship_slug=req.ship_slug,
            tier=req.tier,
            fuel_slug=req.fuel_slug,
            overdrive_mode=req.overdrive_mode,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return result


@router.get("/{expedition_id}", response_model=ExpeditionRead)
async def get_expedition(
    expedition_id: str,
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> ExpeditionRead:
    """Get expedition details by ID."""
    player_id = f"player_{user.telegram_id}"
    expedition = await expedition_service.get_expedition(expedition_id, db)

    if not expedition or expedition.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expedition not found",
        )

    return ExpeditionRead(
        id=expedition.id,
        ship_id=expedition.ship_id,
        slug=expedition.slug,
        tier=expedition.tier,
        overdrive_mode=expedition.overdrive_mode,
        status=expedition.status,
        started_at=expedition.started_at,
        estimated_end=expedition.estimated_end,
        completed_at=expedition.completed_at,
        loot=expedition.loot,
        xp_reward=expedition.xp_reward,
        damage_occurred=expedition.damage_occurred,
    )


@router.get("/active", response_model=list[ActiveExpeditionRead])
async def list_active_expeditions(
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> list[ActiveExpeditionRead]:
    """List all active (pending/in_progress) expeditions for the player."""
    from datetime import datetime, timezone

    player_id = f"player_{user.telegram_id}"
    expeditions = await expedition_service.get_active_expeditions(player_id, db)

    results = []
    now = datetime.now(timezone.utc)
    for exp in expeditions:
        total_seconds = (exp.estimated_end - exp.started_at).total_seconds()
        elapsed_seconds = (now - exp.started_at).total_seconds()
        progress = min(100.0, max(0.0, (elapsed_seconds / total_seconds) * 100)) if total_seconds > 0 else 0

        results.append(ActiveExpeditionRead(
            id=exp.id,
            slug=exp.slug,
            tier=exp.tier,
            overdrive_mode=exp.overdrive_mode,
            status=exp.status,
            started_at=exp.started_at,
            estimated_end=exp.estimated_end,
            progress_percent=round(progress, 1),
        ))

    return results
