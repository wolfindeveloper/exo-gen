from app.domain.exceptions.base import DomainError


class PlayerNotFoundError(DomainError):
    pass


class PlayerAlreadyExistsError(DomainError):
    pass


class InsufficientFragmentsError(DomainError):
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available
        super().__init__(f"Not enough fragments: required {required}, available {available}")


class InsufficientXgenError(DomainError):
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available
        super().__init__(f"Not enough XGen: required {required}, available {available}")


class DailyLoginAlreadyClaimedError(DomainError):
    pass
