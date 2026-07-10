from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities.base import AggregateRoot


@dataclass
class Zone(AggregateRoot):
    id: UUID
    name: str
    description: str
    image_url: str
    fuel_cost: float
    optimism_risk: float
    duration_seconds: int
    loot_table: list[dict] | None = None
    tier: int = 1
    deleted_at: datetime | None = None

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        image_url: str | None = None,
        fuel_cost: float | None = None,
        optimism_risk: float | None = None,
        duration_seconds: int | None = None,
        loot_table: list[dict] | None = None,
        tier: int | None = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if image_url is not None:
            self.image_url = image_url
        if fuel_cost is not None:
            self.fuel_cost = fuel_cost
        if optimism_risk is not None:
            self.optimism_risk = optimism_risk
        if duration_seconds is not None:
            self.duration_seconds = duration_seconds
        if loot_table is not None:
            self.loot_table = loot_table
        if tier is not None:
            self.tier = tier

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None