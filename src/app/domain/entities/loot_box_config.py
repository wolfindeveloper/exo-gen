from dataclasses import dataclass, field
from uuid import UUID

from app.domain.value_objects.loot_box import LootBoxType, LootBoxEntry


@dataclass
class LootBoxConfig:
    id: UUID
    box_type: LootBoxType
    name: str
    description: str
    entries: list[LootBoxEntry] = field(default_factory=list)
    is_active: bool = True
