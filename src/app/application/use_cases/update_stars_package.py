from uuid import UUID

from app.domain.entities.stars_package import StarsPackage
from app.domain.uow import UnitOfWork
from app.domain.repositories.stars_repository import StarsPackageRepository
from app.domain.exceptions.stars import StarsPackageNotFoundError
from app.application.dtos.admin_dto import UpdateStarsPackageDTO


class UpdateStarsPackageUseCase:
    def __init__(self, package_repo: StarsPackageRepository):
        self.package_repo = package_repo

    async def execute(self, package_id: UUID, dto: UpdateStarsPackageDTO, uow: UnitOfWork) -> StarsPackage:
        package = await self.package_repo.get_by_id(package_id)
        if not package or package.is_deleted():
            raise StarsPackageNotFoundError(package_id)

        package.update(**dto.model_dump(exclude_none=True))

        uow.track(package)
        await self.package_repo.save(package)
        await uow.commit()
        return package
