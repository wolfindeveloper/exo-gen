import uuid

from app.domain.entities.stars_package import StarsPackage
from app.domain.uow import UnitOfWork
from app.domain.repositories.stars_repository import StarsPackageRepository
from app.application.dtos.admin_dto import CreateStarsPackageDTO


class CreateStarsPackageUseCase:
    def __init__(self, package_repo: StarsPackageRepository):
        self.package_repo = package_repo

    async def execute(self, dto: CreateStarsPackageDTO, uow: UnitOfWork) -> StarsPackage:
        package = StarsPackage(
            id=uuid.uuid4(),
            stars_amount=dto.stars_amount,
            xgen_reward=dto.xgen_reward,
            is_active=dto.is_active,
        )

        await self.package_repo.save(package)
        await uow.commit()

        return package
