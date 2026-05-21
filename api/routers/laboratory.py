"""Laboratory router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.middleware.auth import TelegramUser, get_current_player
from api.schemas.laboratory import CraftRequest, CraftResponse, RecipeInfo
from api.services import laboratory_service
from core.database import get_db
from core.config_loader import load_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/laboratory", tags=["laboratory"])


@router.post("/craft", response_model=CraftResponse, status_code=status.HTTP_201_CREATED)
async def craft_artifact(
    req: CraftRequest,
    user: TelegramUser = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
) -> CraftResponse:
    """Attempt to craft an artifact from essences.

    $XGEN is burned 100%. Essences are consumed 100% on success,
    or refunded 50% on failure (hash collision).
    """
    player_id = f"player_{user.telegram_id}"

    try:
        result = await laboratory_service.attempt_craft(
            player_id=player_id,
            domain_slug=req.domain_slug,
            essences=req.essences,
            xgen_amount=req.xgen_amount,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CraftResponse(**result)


@router.get("/domains")
async def list_domains() -> list[dict]:
    """Return all available galaxy zones for laboratory crafting."""
    galaxy_config = load_config("galaxy_zones")
    zones = galaxy_config.get("galaxy_zones", {})

    return [
        {
            "slug": zone.get("slug", key),
            "name": zone.get("name", {}),
            "tier": zone.get("tier", 0),
            "image_path": zone.get("image_path", ""),
        }
        for key, zone in zones.items()
    ]


@router.get("/recipes/{recipe_hash}", response_model=RecipeInfo | None)
async def get_recipe_info(
    recipe_hash: str,
    db: AsyncSession = Depends(get_db),
) -> dict | None:
    """Return public recipe info by hash (for marketplace verification)."""
    info = await laboratory_service.get_recipe_info(recipe_hash, db)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )
    return info
