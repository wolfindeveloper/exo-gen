from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID

from app.application.dtos.admin_dto import LootDropEntry


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
    loot_table: list[LootDropEntry]

    @field_validator("loot_table", mode="after")
    @classmethod
    def validate_loot_table(cls, v: list[LootDropEntry]) -> list[LootDropEntry]:
        if not v:
            raise ValueError("Loot table cannot be empty")
        return v


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