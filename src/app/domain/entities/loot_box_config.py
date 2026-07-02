from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from app.domain.value_objects.loot_box import LootBoxEntry


@dataclass
class LootBoxConfig:
    id: UUID
    box_type: str
    name: str
    description: str
    entries: list[LootBoxEntry] = field(default_factory=list)
    is_active: bool = True
    deleted_at: datetime | None = None

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        entries: list[LootBoxEntry] | None = None,
        is_active: bool | None = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if entries is not None:
            self.entries = entries
        if is_active is not None:
            self.is_active = is_active

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None
