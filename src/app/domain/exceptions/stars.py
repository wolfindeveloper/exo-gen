from uuid import UUID

from app.domain.exceptions.base import DomainError


class StarsPackageNotFoundError(DomainError):
    def __init__(self, package_id: UUID):
        self.package_id = package_id
        super().__init__(f"Stars package {package_id} not found")


class TransactionAlreadyProcessedError(DomainError):
    def __init__(self, telegram_charge_id: str):
        self.telegram_charge_id = telegram_charge_id
        super().__init__(f"Transaction {telegram_charge_id} already processed")
