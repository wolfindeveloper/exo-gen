from app.domain.exceptions.base import DomainError


class ItemInUseInInventoryError(DomainError):
    def __init__(self, item_name: str, count: int):
        super().__init__(f"Cannot delete item '{item_name}': used in {count} player inventories")


class ItemUsedInActiveZoneError(DomainError):
    def __init__(self, item_name: str, zone_count: int):
        super().__init__(f"Cannot delete item '{item_name}': used in loot table of {zone_count} active zones")


class ItemListedInShopError(DomainError):
    def __init__(self, item_name: str, shop_count: int):
        super().__init__(f"Cannot delete item '{item_name}': listed in {shop_count} active shop items")
