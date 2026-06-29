from app.application.dtos.stars_dto import BuyXgenRequestDTO, BuyXgenResponseDTO
from app.domain.entities.player import Player
from app.domain.repositories.stars_repository import StarsPackageRepository
from app.domain.exceptions.stars import StarsPackageNotFoundError
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService


class BuyXgenUseCase:
    def __init__(
        self,
        stars_package_repo: StarsPackageRepository,
        telegram_bot_service: TelegramBotService,
    ):
        self.stars_package_repo = stars_package_repo
        self.telegram_bot_service = telegram_bot_service

    async def execute(
        self, player: Player, dto: BuyXgenRequestDTO
    ) -> BuyXgenResponseDTO:
        package = await self.stars_package_repo.get_by_id(dto.package_id)
        if not package or not package.is_active:
            raise StarsPackageNotFoundError(dto.package_id)

        payload = f"{player.id}:{package.id}"
        title = f"{package.xgen_reward} XGen"
        description = f"Get {package.xgen_reward} XGen for {package.stars_amount} Stars"
        prices = [{"label": title, "amount": package.stars_amount}]

        invoice_url = await self.telegram_bot_service.create_invoice_link(
            title=title,
            description=description,
            prices=prices,
            payload=payload,
        )

        return BuyXgenResponseDTO(
            invoice_url=invoice_url,
            package_id=package.id,
        )
