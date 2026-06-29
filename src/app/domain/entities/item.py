from dataclasses import dataclass, field
from uuid import UUID
from enum import Enum

class ItemType(str, Enum):
    CONSUMABLE = "consumable"  # Расходники (чай, ремкомплекты)
    ARTIFACT = "artifact"      # Артефакты (дают пассивные бонусы)
    MATERIAL = "material"      # Материалы (для будущих крафтов)
    KEY_ITEM = "key_item"      # Ключевые предметы (для открытия статей/дверей)
    LOOT_BOX = "loot_box"      # Лутбоксы (покупаются в магазине, открываются через OpenLootBoxUseCase)

@dataclass
class Item:
    id: UUID
    name: str
    description: str
    type: ItemType
    rarity: str = "common"
    
    # JSON-словарь с эффектами. Например: {"restore_tea": 50} или {"bonus_luck": 0.1}
    # В БД это будет колонка типа JSONB
    effect: dict = field(default_factory=dict)
    
    # Можно ли продать этот предмет в магазине (в будущем)
    is_tradable: bool = False 
    sell_price: int = 0