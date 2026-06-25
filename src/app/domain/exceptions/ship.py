from app.domain.exceptions.base import DomainError


class ShipNotFoundError(DomainError):
    pass


class InsufficientTeaError(DomainError):
    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        super().__init__(f"Not enough tea: required {required}, available {available}")


class ShipAlreadyInExpeditionError(DomainError):
    pass


class ShipDestroyedError(DomainError):
    pass
