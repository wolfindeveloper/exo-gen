from app.domain.exceptions.base import DomainError


class ZoneNotFoundError(DomainError):
    pass


class ZoneHasActiveExpeditionsError(DomainError):
    def __init__(self, zone_name: str):
        super().__init__(f"Cannot delete zone '{zone_name}': there are active expeditions in this zone")
