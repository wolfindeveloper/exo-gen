from app.application.dtos.stars_dto import StarsPackageResponseDTO
from app.domain.repositories.stars_repository import StarsPackageRepository


class GetStarsPackagesUseCase:
    def __init__(self, stars_package_repo: StarsPackageRepository):
        self.stars_package_repo = stars_package_repo

    async def execute(self) -> list[StarsPackageResponseDTO]:
        packages = await self.stars_package_repo.get_all_active()
        return [StarsPackageResponseDTO(
            id=p.id,
            stars_amount=p.stars_amount,
            xgen_reward=p.xgen_reward,
            is_active=p.is_active,
        ) for p in packages]
