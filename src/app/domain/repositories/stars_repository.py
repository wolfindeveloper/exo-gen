from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.stars_package import StarsPackage
from app.domain.entities.transaction import Transaction


class StarsPackageRepository(ABC):
    @abstractmethod
    async def get_by_id(self, package_id: UUID) -> StarsPackage | None:
        pass

    @abstractmethod
    async def get_all_active(self) -> list[StarsPackage]:
        pass

    @abstractmethod
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[StarsPackage], int]:
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

    @abstractmethod
    async def insert_if_not_exists(self, transaction: Transaction) -> bool:
        """Insert transaction with ON CONFLICT DO NOTHING on telegram_charge_id.

        Returns True if inserted, False if conflict (already exists).
        """
        pass
