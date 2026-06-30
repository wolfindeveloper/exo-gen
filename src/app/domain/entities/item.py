from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID
from enum import Enum

class ItemType(str, Enum):
    CONSUMABLE = "consumable"
    ARTIFACT = "artifact"
    MATERIAL = "material"
    KEY_ITEM = "key_item"
    LOOT_BOX = "loot_box"

@dataclass
class Item:
    id: UUID
    name: str
    description: str
    type: ItemType
    rarity: str = "common"
    effect: dict = field(default_factory=dict)
    is_tradable: bool = False
    sell_price: int = 0
    deleted_at: datetime | None = None

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        rarity: str | None = None,
        effect: dict | None = None,
        is_tradable: bool | None = None,
        sell_price: int | None = None,
        **kwargs: object,
    ) -> None:
        if "type" in kwargs:
            raise ValueError("Cannot change item type after creation")
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if rarity is not None:
            self.rarity = rarity
        if effect is not None:
            self.effect = effect
        if is_tradable is not None:
            self.is_tradable = is_tradable
        if sell_price is not None:
            self.sell_price = sell_price

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None


@dataclass
class ItemUsageReport:
    item_id: UUID
    inventory_count: int = 0
    zone_names: list[str] = field(default_factory=list)
    loot_box_names: list[str] = field(default_factory=list)
    active_shop_items: int = 0

    @property
    def in_use(self) -> bool:
        return bool(
            self.inventory_count > 0
            or self.zone_names
            or self.loot_box_names
            or self.active_shop_items > 0
        )