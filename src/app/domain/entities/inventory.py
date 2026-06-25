from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.entities.inventory_item import InventoryItem
from app.domain.exceptions.inventory import ItemNotInInventoryError, InsufficientItemQuantityError

@dataclass
class Inventory:
    player_id: UUID
    items: list[InventoryItem] = field(default_factory=list)

    def add_item(self, item_id: UUID, quantity: int = 1) -> InventoryItem:
        """Добавляет предмет. Если такой уже есть - увеличивает количество (стакует)."""
        existing = next((i for i in self.items if i.item_id == item_id), None)
        
        if existing:
            existing.add_quantity(quantity)
            return existing
        
        new_item = InventoryItem(
            id=uuid4(),
            player_id=self.player_id,
            item_id=item_id,
            quantity=quantity
        )
        self.items.append(new_item)
        return new_item

    def remove_item(self, item_id: UUID, quantity: int = 1) -> None:
        """Списывает предмет. Если количество падает до 0 - удаляет из списка."""
        existing = next((i for i in self.items if i.item_id == item_id), None)
        if not existing:
            raise ItemNotInInventoryError(item_id)

        if existing.quantity < quantity:
            raise InsufficientItemQuantityError(item_id, required=quantity, available=existing.quantity)

        existing.remove_quantity(quantity)

        if existing.quantity == 0:
            self.items.remove(existing)

    def has_item(self, item_id: UUID, quantity: int = 1) -> bool:
        """Проверяет наличие предмета (нужно для открытия статей)"""
        existing = next((i for i in self.items if i.item_id == item_id), None)
        return existing is not None and existing.quantity >= quantity