from uuid import UUID

from app.domain.exceptions.base import DomainError


class EquipmentNotFoundError(DomainError):
    def __init__(self, ship_id: UUID):
        self.ship_id = ship_id
        super().__init__(f"Equipment not found for ship {ship_id}")


class ArtifactNotEquippedError(DomainError):
    def __init__(self, item_id: UUID):
        self.item_id = item_id
        super().__init__(f"Artifact {item_id} is not equipped on this ship")


class ArtifactAlreadyEquippedError(DomainError):
    def __init__(self, item_id: UUID):
        self.item_id = item_id
        super().__init__(f"Artifact {item_id} is already equipped on this ship. Duplicate artifacts are not supported.")


class SlotLockedByLevelError(DomainError):
    def __init__(self, slot_index: int, required_level: int, current_level: int, max_slots: int):
        self.slot_index = slot_index
        self.required_level = required_level
        self.current_level = current_level
        self.max_slots = max_slots
        super().__init__(
            f"Slot {slot_index} requires level {required_level}. "
            f"Current level {current_level}, max slots {max_slots}"
        )
