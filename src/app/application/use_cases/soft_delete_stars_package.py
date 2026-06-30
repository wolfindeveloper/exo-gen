from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.stars_repository import StarsPackageRepository
from app.domain.exceptions.stars import StarsPackageNotFoundError


class SoftDeleteStarsPackageUseCase:
    def __init__(self, package_repo: StarsPackageRepository):
        self.package_repo = package_repo

    async def execute(self, package_id: UUID, uow: UnitOfWork) -> None:
        package = await self.package_repo.get_by_id(package_id)
        if not package or package.is_deleted():
            raise StarsPackageNotFoundError(package_id)

        package.soft_delete()
        uow.track(package)
        await self.package_repo.save(package)
        await uow.commit()
