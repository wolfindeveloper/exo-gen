from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.equipment_repository import EquipmentRepository
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.exceptions.equipment import EquipmentNotFoundError, ArtifactNotEquippedError
from app.application.dtos.equipment_dto import UnequipArtifactDTO, EquipArtifactResponseDTO, EquipmentResponseDTO, EquippedArtifactDTO


class UnequipArtifactUseCase:
    def __init__(
        self,
        inventory_repo: InventoryRepository,
        equipment_repo: EquipmentRepository,
    ):
        self.inventory_repo = inventory_repo
        self.equipment_repo = equipment_repo

    async def execute(self, player: Player, dto: UnequipArtifactDTO, uow: UnitOfWork) -> EquipArtifactResponseDTO:
        ship = next((s for s in player.ships if s.id == dto.ship_id), None)
        if not ship:
            raise ShipNotFoundError("Ship not found or does not belong to player")

        equipment = await self.equipment_repo.get_by_ship_id(ship.id)
        if not equipment:
            raise EquipmentNotFoundError(ship.id)

        try:
            unequipped = equipment.unequip(dto.item_id)
        except ValueError:
            raise ArtifactNotEquippedError(dto.item_id)

        inventory = await self.inventory_repo.get_by_player_id(player.id)
        inventory.add_item(unequipped.item_id, quantity=1)

        uow.track(equipment)
        await self.equipment_repo.save(equipment)
        await self.inventory_repo.save(inventory)
        await uow.commit()

        return EquipArtifactResponseDTO(
            message=f"Unequipped artifact {dto.item_id} from {ship.name}",
            equipment=self._equipment_to_dto(equipment),
        )

    def _equipment_to_dto(self, equipment) -> EquipmentResponseDTO:
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
