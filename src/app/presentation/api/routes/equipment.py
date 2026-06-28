from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.equipment_repository import EquipmentRepository
from app.application.use_cases.equip_artifact import EquipArtifactUseCase
from app.application.use_cases.unequip_artifact import UnequipArtifactUseCase
from app.application.dtos.equipment_dto import (
    EquipArtifactDTO,
    UnequipArtifactDTO,
    EquipArtifactResponseDTO,
    EquipmentResponseDTO,
    EquippedArtifactDTO,
)
from app.domain.entities.player import Player
from app.domain.exceptions import DomainError
from app.domain.uow import UnitOfWork
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import get_item_repo, get_inventory_repo, get_equipment_repo, get_uow

router = APIRouter(tags=["Equipment"])


@router.get("/equipment/{ship_id}", response_model=EquipmentResponseDTO)
async def get_equipment(
    ship_id: UUID,
    current_player: Player = Depends(get_current_player),
    equipment_repo: EquipmentRepository = Depends(get_equipment_repo),
):
    ship = next((s for s in current_player.ships if s.id == ship_id), None)
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")

    equipment = await equipment_repo.get_by_ship_id(ship_id)
    if not equipment:
        return EquipmentResponseDTO(ship_id=ship_id, artifacts=[])

    return EquipmentResponseDTO(
        ship_id=equipment.ship_id,
        artifacts=[
            EquippedArtifactDTO(
                item_id=a.item_id,
                slot_type=a.slot_type.value,
                bonuses=a.bonuses,
            )
            for a in equipment.artifacts
        ],
    )


@router.post("/equipment/equip", response_model=EquipArtifactResponseDTO)
async def equip_artifact(
    dto: EquipArtifactDTO,
    current_player: Player = Depends(get_current_player),
    item_repo: ItemRepository = Depends(get_item_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    equipment_repo: EquipmentRepository = Depends(get_equipment_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = EquipArtifactUseCase(item_repo, inventory_repo, equipment_repo)
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/equipment/unequip", response_model=EquipArtifactResponseDTO)
async def unequip_artifact(
    dto: UnequipArtifactDTO,
    current_player: Player = Depends(get_current_player),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    equipment_repo: EquipmentRepository = Depends(get_equipment_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = UnequipArtifactUseCase(inventory_repo, equipment_repo)
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
