from app.domain.exceptions.base import DomainError


class ZoneNotFoundError(DomainError):
    pass


class ZoneHasActiveExpeditionsError(DomainError):
    def __init__(self, zone_name: str):
        super().__init__(f"Cannot delete zone '{zone_name}': there are active expeditions in this zone")


class ZoneLockedByLevelError(DomainError):
    def __init__(self, zone_name: str, required_level: int, current_level: int):
        self.zone_name = zone_name
        self.required_level = required_level
        self.current_level = current_level
        super().__init__(
            f"Zone '{zone_name}' requires level {required_level}, "
            f"current level is {current_level}"
        )
