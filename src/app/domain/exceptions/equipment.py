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
