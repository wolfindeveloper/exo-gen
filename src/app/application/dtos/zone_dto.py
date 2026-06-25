from pydantic import BaseModel, ConfigDict
from uuid import UUID

class LootItemDTO(BaseModel):
    item_type: str
    amount: int
    chance: float
    item_id: str | None = None


class CreateZoneDTO(BaseModel):
    name: str
    description: str
    image_url: str
    fuel_cost: float
    optimism_risk: float
    duration_seconds: int
    loot_table: list[LootItemDTO]


class ZoneResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    image_url: str
    fuel_cost: float
    optimism_risk: float
    duration_seconds: int
    loot_table: list[LootItemDTO]