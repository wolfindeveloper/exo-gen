from dataclasses import dataclass, field
from uuid import UUID

@dataclass
class InventoryItem:
    id: UUID
    player_id: UUID      # Чей это предмет
    item_id: UUID        # Ссылка на справочник Item
    quantity: int = 1
    
    # Уникальные свойства конкретного экземпляра (например, уровень заточки артефакта)
    metadata: dict = field(default_factory=dict)

    def add_quantity(self, amount: int) -> None:
        self.quantity += amount

    def remove_quantity(self, amount: int) -> None:
        if self.quantity < amount:
            raise ValueError("Not enough items in inventory")
        self.quantity -= amount