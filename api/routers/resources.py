"""Resource router: repair ships, convert repair mats."""

import logging
import math

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.middleware.auth import get_current_player
from api.services.ship_service import get_ship_repair_info, repair_ship
from core.config_loader import load_config
from core.database import get_db
from core.models import PlayerInventory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resources", tags=["resources"])


class RepairRequest(BaseModel):
    """Request to repair a ship."""
    ship_id: str


class ConvertRequest(BaseModel):
    """Request to convert higher-tier repair mats to lower-tier."""
    source_tier: int
    amount: int


class RepairInfoResponse(BaseModel):
    """Response with ship repair info."""
    ship_id: str
    stability: int
    ship_tier: int
    mat_slug: str
    mat_name: str
    repair_value: int
    required_mats: int
    owned_mats: int
    can_repair: bool


class ConvertResponse(BaseModel):
    """Response after converting mats."""
    converted: int
    source_slug: str
    target_slug: str
    target_amount: int


@router.post("/repair", response_model=dict)
async def repair_ship_endpoint(
    request: RepairRequest,
    player=Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Repair a ship using tier-matching repair materials.

    Deducts repair mats from inventory and restores ship stability to 100%.
    """
    try:
        result = await repair_ship(player["id"], request.ship_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/repair/{ship_id}", response_model=RepairInfoResponse)
async def get_repair_info(
    ship_id: str,
    player=Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Get repair info for a ship: stability, required mats, owned mats."""
    try:
        info = await get_ship_repair_info(player["id"], ship_id, db)
        return RepairInfoResponse(**info)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/convert", response_model=ConvertResponse)
async def convert_mats(
    request: ConvertRequest,
    player=Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Convert higher-tier repair mats to lower-tier.

    Rate: 1x Tier N → 2x Tier N-1.
    Prevents conversion below T1.
    """
    if request.source_tier < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя конвертировать материалы T1",
        )

    if request.source_tier > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Максимальный тир — 5",
        )

    if request.amount < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество должно быть больше 0",
        )

    source_slug = f"repair_matter_t{request.source_tier}"
    target_slug = f"repair_matter_t{request.source_tier - 1}"
    target_amount = request.amount * 2

    # Validate repair mats config exists
    repair_mats = load_config("repair_mats")
    if source_slug not in repair_mats or target_slug not in repair_mats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый тир ремнабора",
        )

    # Check player has enough source mats
    from sqlalchemy import select

    result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player["id"],
            PlayerInventory.slug == source_slug,
            PlayerInventory.quantity >= request.amount,
        )
    )
    source_item = result.scalar_one_or_none()

    if not source_item:
        any_result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == player["id"],
                PlayerInventory.slug == source_slug,
            )
        )
        any_item = any_result.scalar_one_or_none()
        owned = any_item.quantity if any_item else 0
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недостаточно ремнаборов T{request.source_tier}. Требуется: {request.amount}, есть: {owned}",
        )

    # Deduct source, add target
    source_item.quantity -= request.amount

    target_result = await db.execute(
        select(PlayerInventory).where(
            PlayerInventory.player_id == player["id"],
            PlayerInventory.slug == target_slug,
        )
    )
    target_item = target_result.scalar_one_or_none()

    if target_item:
        target_item.quantity += target_amount
    else:
        db.add(PlayerInventory(
            id=str(__import__("uuid").uuid4()),
            player_id=player["id"],
            slug=target_slug,
            quantity=target_amount,
        ))

    await db.flush()

    logger.info(
        "Converted %d x %s → %d x %s for player %s",
        request.amount,
        source_slug,
        target_amount,
        target_slug,
        player["id"],
    )

    return ConvertResponse(
        converted=request.amount,
        source_slug=source_slug,
        target_slug=target_slug,
        target_amount=target_amount,
    )
