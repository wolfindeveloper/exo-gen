from dataclasses import dataclass
from uuid import UUID


@dataclass
class Zone:
    id: UUID
    name: str
    description: str
    image_url: str
    fuel_cost: float
    optimism_risk: float
    duration_seconds: int
    loot_table: list[dict] | None = None