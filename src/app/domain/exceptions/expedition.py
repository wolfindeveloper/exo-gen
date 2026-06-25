from app.domain.exceptions.base import DomainError


class ExpeditionNotFoundError(DomainError):
    pass


class ExpeditionNotFinishedError(DomainError):
    pass


class ExpeditionAlreadyClaimedError(DomainError):
    pass
