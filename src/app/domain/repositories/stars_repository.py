from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.stars_package import StarsPackage
from app.domain.entities.transaction import Transaction, TransactionStatus


class StarsPackageRepository(ABC):
    @abstractmethod
    async def get_by_id(self, package_id: UUID) -> StarsPackage | None:
        pass

    @abstractmethod
    async def get_all_active(self) -> list[StarsPackage]:
        pass

    @abstractmethod
    async def save(self, package: StarsPackage) -> None:
        pass


class TransactionRepository(ABC):
    @abstractmethod
    async def get_by_telegram_charge_id(self, telegram_charge_id: str) -> Transaction | None:
        pass

    @abstractmethod
    async def save(self, transaction: Transaction) -> None:
        pass
