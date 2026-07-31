from pydantic import BaseModel
from uuid import UUID


class EquipArtifactDTO(BaseModel):
    ship_id: UUID
    item_id: UUID
    slot_index: int


class UnequipArtifactDTO(BaseModel):
    ship_id: UUID
    item_id: UUID


class EquippedArtifactDTO(BaseModel):
    item_id: UUID
    bonuses: dict


class EquipmentResponseDTO(BaseModel):
    ship_id: UUID
    artifacts: list[EquippedArtifactDTO | None]


class EquipArtifactResponseDTO(BaseModel):
    message: str
    equipment: EquipmentResponseDTO
