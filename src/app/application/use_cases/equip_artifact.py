from app.domain.entities.player import Player
from app.domain.entities.item import ItemType
from app.domain.entities.equipment import Equipment
from app.domain.value_objects.equipment import SlotType
from app.domain.uow import UnitOfWork
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.equipment_repository import EquipmentRepository
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.exceptions.inventory import ItemNotFoundError, ItemNotInInventoryError
from app.application.dtos.equipment_dto import EquipArtifactDTO, EquipArtifactResponseDTO, EquipmentResponseDTO, EquippedArtifactDTO


SLOT_TYPE_MAP: dict[str, SlotType] = {
    "bonus_speed": SlotType.SPEED,
    "bonus_defense": SlotType.DEFENSE,
    "bonus_capacity": SlotType.CAPACITY,
    "bonus_luck": SlotType.LUCK,
    "bonus_fuel": SlotType.FUEL_EFFICIENCY,
    "bonus_xp": SlotType.XP_BOOST,
    "bonus_fragment": SlotType.FRAGMENT_BOOST,
}


class EquipArtifactUseCase:
    def __init__(
        self,
        item_repo: ItemRepository,
        inventory_repo: InventoryRepository,
        equipment_repo: EquipmentRepository,
    ):
        self.item_repo = item_repo
        self.inventory_repo = inventory_repo
        self.equipment_repo = equipment_repo

    async def execute(self, player: Player, dto: EquipArtifactDTO, uow: UnitOfWork) -> EquipArtifactResponseDTO:
        ship = next((s for s in player.ships if s.id == dto.ship_id), None)
        if not ship:
            raise ShipNotFoundError("Ship not found or does not belong to player")

        item = await self.item_repo.get_by_id(dto.item_id)
        if not item:
            raise ItemNotFoundError(dto.item_id)

        if item.type != ItemType.ARTIFACT:
            raise ValueError("Item is not an artifact")

        inventory = await self.inventory_repo.get_by_player_id(player.id)
        if not inventory.has_item(item.id):
            raise ItemNotInInventoryError(item.id)

        slot_type = self._determine_slot_type(item.effect)
        bonuses = self._extract_bonuses(item.effect)

        equipment = await self.equipment_repo.get_by_ship_id(ship.id)
        if not equipment:
            equipment = Equipment(ship_id=ship.id)

        replaced = equipment.equip(item.id, slot_type, bonuses)

        inventory.remove_item(item.id, quantity=1)
        if replaced is not None:
            inventory.add_item(replaced.item_id, quantity=1)

        uow.track(equipment)
        await self.equipment_repo.save(equipment)
        await self.inventory_repo.save(inventory)
        await uow.commit()

        return EquipArtifactResponseDTO(
            message=f"Equipped {item.name} on {ship.name}",
            equipment=self._equipment_to_dto(equipment),
        )

    def _determine_slot_type(self, effect: dict) -> SlotType:
        for key, slot_type in SLOT_TYPE_MAP.items():
            if key in effect:
                return slot_type
        raise ValueError("Artifact effect must contain at least one bonus_* key to determine slot type")

    def _extract_bonuses(self, effect: dict) -> dict:
        bonuses: dict[str, float] = {}
        for key, value in effect.items():
            if key.startswith("bonus_") and isinstance(value, (int, float)):
                stat_key = key.replace("bonus_", "")
                bonuses[stat_key] = float(value)
        return bonuses

    def _equipment_to_dto(self, equipment: Equipment) -> EquipmentResponseDTO:
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
