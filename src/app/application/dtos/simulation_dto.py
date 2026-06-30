from uuid import UUID

from pydantic import BaseModel, Field


class SimulateLootRequestDTO(BaseModel):
    count: int = Field(100, ge=1, le=10000)


class LootSimulationResultDTO(BaseModel):
    drop_type: str
    item_id: UUID | None = None
    item_name: str | None = None
    total_dropped: int
    percentage: float


class LootBoxSimulationResultDTO(BaseModel):
    drop_type: str
    item_id: UUID | None = None
    item_name: str | None = None
    total_dropped: int
    percentage: float
    total_xgen: int | None = None
    total_fragments: int | None = None
