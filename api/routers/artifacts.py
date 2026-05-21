"""Artifact router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.middleware.auth import TelegramUser, get_current_player
from api.schemas.artifact import (
    ArtifactRead,
    CalibrateResponse,
    ClaimYieldResponse,
    StakeResponse,
)
from api.services import erosion_yield_service
from core.database import get_db
from core.models import Artifact

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("", response_model=list[ArtifactRead])
async def list_artifacts(
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> list[ArtifactRead]:
    """List all artifacts owned by the player."""
    player_id = f"player_{user.telegram_id}"
    result = await db.execute(
        select(Artifact).where(Artifact.player_id == player_id).order_by(Artifact.created_at.desc())
    )
    artifacts = result.scalars().all()

    return [
        ArtifactRead(
            id=a.id,
            slug=a.slug,
            recipe_hash=a.recipe_hash,
            status=a.status,
            cycles_remaining=a.cycles_remaining,
            staked_at=a.staked_at,
            accumulated_yield=a.accumulated_yield,
            bonus_multiplier=a.bonus_multiplier,
            domain_slug=a.domain_slug,
            created_at=a.created_at,
        )
        for a in artifacts
    ]


@router.post("/{artifact_id}/stake", response_model=StakeResponse)
async def stake_artifact(
    artifact_id: str,
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> StakeResponse:
    """Stake an artifact for passive yield generation."""
    from datetime import datetime, timezone

    player_id = f"player_{user.telegram_id}"
    artifact = await db.get(Artifact, artifact_id)

    if not artifact or artifact.player_id != player_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    if artifact.status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active artifacts can be staked",
        )
    if artifact.staked_at:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Artifact is already staked",
        )

    artifact.staked_at = datetime.now(timezone.utc)
    await db.flush()

    return StakeResponse(
        artifact_id=artifact_id,
        staked=True,
        message="Artifact staked successfully",
    )


@router.post("/{artifact_id}/unstake", response_model=StakeResponse)
async def unstake_artifact(
    artifact_id: str,
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> StakeResponse:
    """Unstake an artifact, stopping yield generation."""
    player_id = f"player_{user.telegram_id}"
    artifact = await db.get(Artifact, artifact_id)

    if not artifact or artifact.player_id != player_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    if not artifact.staked_at:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Artifact is not staked",
        )

    artifact.staked_at = None
    await db.flush()

    return StakeResponse(
        artifact_id=artifact_id,
        staked=False,
        message="Artifact unstaked successfully",
    )


@router.post("/{artifact_id}/claim-yield", response_model=ClaimYieldResponse)
async def claim_yield(
    artifact_id: str,
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> ClaimYieldResponse:
    """Claim accumulated staking yield and transfer $XGEN to player balance."""
    from datetime import datetime, timezone

    player_id = f"player_{user.telegram_id}"
    artifact = await db.get(Artifact, artifact_id)

    if not artifact or artifact.player_id != player_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    if not artifact.staked_at:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Artifact must be staked to claim yield",
        )

    yield_data = await erosion_yield_service.calculate_staking_yield(
        player_id, artifact_id, db
    )
    claimed = yield_data["pending_yield"]

    if claimed <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No yield available to claim",
        )

    from core.models import Player
    player = await db.get(Player, player_id)
    if player:
        player.xgen_balance += int(claimed)

    artifact.accumulated_yield = 0.0
    artifact.last_yield_claim = datetime.now(timezone.utc)
    await db.flush()

    return ClaimYieldResponse(
        artifact_id=artifact_id,
        claimed_amount=round(claimed, 4),
        new_accumulated=0.0,
    )


@router.post("/{artifact_id}/calibrate", response_model=CalibrateResponse)
async def calibrate_artifact(
    artifact_id: str,
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> CalibrateResponse:
    """Recalibrate a dormant or worn artifact. Resets cycles, deducts cost."""
    player_id = f"player_{user.telegram_id}"

    try:
        result = await erosion_yield_service.calibrate_artifact(
            artifact_id, player_id, db
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return CalibrateResponse(**result)
