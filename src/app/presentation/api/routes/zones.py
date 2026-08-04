from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.application.dtos.zone_dto import ZoneResponseDTO
from app.application.dtos.zone_preview_dto import ZonePreviewDTO
from app.application.use_cases.get_zones import GetZonesUseCase
from app.application.use_cases.get_zone_preview import GetZonePreviewUseCase
from app.domain.entities.player import Player
from app.domain.exceptions import DomainError
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.equipment_repository import EquipmentRepository
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import (
    get_item_repo,
    get_zone_repo,
    get_equipment_repo,
    require_telegram_user,
)

router = APIRouter(
    prefix="/zones",
    tags=["Zones"],
    dependencies=[Depends(require_telegram_user)],
)


@router.get("/", response_model=list[ZoneResponseDTO])
async def get_zones(
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
):
    use_case = GetZonesUseCase(zone_repo=zone_repo, item_repo=item_repo)
    return await use_case.execute()


class ZonePreviewParams(BaseModel):
    ship_id: UUID


@router.get("/{zone_id}/preview", response_model=ZonePreviewDTO)
async def get_zone_preview(
    zone_id: UUID,
    ship_id: UUID,
    current_player: Player = Depends(get_current_player),
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    equipment_repo: EquipmentRepository = Depends(get_equipment_repo),
):
    use_case = GetZonePreviewUseCase(
        zone_repo=zone_repo,
        equipment_repo=equipment_repo,
    )
    try:
        return await use_case.execute(current_player, zone_id, ship_id)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
