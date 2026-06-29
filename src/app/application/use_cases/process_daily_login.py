from app.domain.exceptions.player import PlayerNotFoundError
from app.domain.uow import UnitOfWork
from app.domain.value_objects.loot_box import LootBoxType
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.services.loot_box_service import LootBoxService
from app.application.dtos.daily_login_dto import DailyLoginResponseDTO
from app.application.use_cases.open_loot_box import OpenLootBoxUseCase


class ProcessDailyLoginUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        loot_box_service: LootBoxService,
        loot_box_repo: LootBoxRepository,
        inventory_repo: InventoryRepository,
        item_repo: ItemRepository,
    ):
        self.player_repo = player_repo
        self.loot_box_service = loot_box_service
        self.loot_box_repo = loot_box_repo
        self.inventory_repo = inventory_repo
        self.item_repo = item_repo

    async def execute(self, telegram_id: int, uow: UnitOfWork) -> DailyLoginResponseDTO:
        player = await self.player_repo.get_by_telegram_id(telegram_id)

        if not player:
            raise PlayerNotFoundError(
                f"Player with telegram_id {telegram_id} not found"
            )

        domain_result = player.process_daily_login()
        uow.track(player)

        loot_result = None
        if domain_result.got_box:
            open_box_uc = OpenLootBoxUseCase(
                self.loot_box_service,
                self.loot_box_repo,
                self.inventory_repo,
                self.item_repo,
            )
            loot_result = await open_box_uc.execute(player, LootBoxType.DAILY_42, uow)

        await self.player_repo.save(player)
        await uow.commit()

        return DailyLoginResponseDTO(
            earned_xp=domain_result.earned_xp,
            new_streak=domain_result.new_streak,
            got_box=domain_result.got_box,
            already_claimed=domain_result.already_claimed,
            box_opened=loot_result is not None,
            box_xgen=loot_result.xgen_earned if loot_result else 0,
            box_fragments=loot_result.fragments_earned if loot_result else 0,
            box_items=loot_result.items_earned if loot_result else [],
        )
