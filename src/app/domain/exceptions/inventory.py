from uuid import UUID

from app.domain.exceptions.base import DomainError


class ItemNotFoundError(DomainError):
    def __init__(self, item_id: UUID):
        self.item_id = item_id
        super().__init__(f"Item {item_id} does not exist in catalog")


class ItemNotInInventoryError(DomainError):
    def __init__(self, item_id: UUID):
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found in inventory")


class ItemNotConsumableError(DomainError):
    pass


class InsufficientItemQuantityError(DomainError):
    def __init__(self, item_id: UUID, required: int, available: int):
        self.item_id = item_id
        self.required = required
        self.available = available
        super().__init__(f"Insufficient quantity of item {item_id}: required {required}, available {available}")
