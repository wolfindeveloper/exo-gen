from pydantic import BaseModel, ConfigDict
from uuid import UUID


class RefuelShipDTO(BaseModel):
    ship_id: UUID


class RepairShipDTO(BaseModel):
    ship_id: UUID


class RefuelShipResponseDTO(BaseModel):
    message: str
    item_used_id: UUID
    item_used_name: str
    tea_restored: float
    new_tea_level: float


class RepairShipResponseDTO(BaseModel):
    message: str
    item_used_id: UUID
    item_used_name: str
    optimism_restored: float
    new_optimism_level: float


class EquippedArtifactData(BaseModel):
    item_id: UUID
    slot_type: str
    bonuses: dict


class ShipEquipmentData(BaseModel):
    artifacts: list[EquippedArtifactData]


class ShipResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    tea_level: float
    optimism: float
    speed: float
    defense: float
    luck: float
    equipment: ShipEquipmentData | None = None
