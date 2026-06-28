from app.domain.exceptions.player import PlayerNotFoundError
from app.domain.uow import UnitOfWork
from app.domain.value_objects.loot_box import LootBoxType
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService
from app.application.dtos.daily_login_dto import DailyLoginResponseDTO
from app.application.use_cases.open_loot_box import OpenLootBoxUseCase


class ProcessDailyLoginUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        loot_box_service: LootBoxService | None = None,
        loot_box_repo: LootBoxRepository | None = None,
        inventory_repo: InventoryRepository | None = None,
    ):
        self.player_repo = player_repo
        self.loot_box_service = loot_box_service
        self.loot_box_repo = loot_box_repo
        self.inventory_repo = inventory_repo

    async def execute(self, telegram_id: int, uow: UnitOfWork) -> DailyLoginResponseDTO:
        player = await self.player_repo.get_by_telegram_id(telegram_id)

        if not player:
            raise PlayerNotFoundError(
                f"Player with telegram_id {telegram_id} not found"
            )

        domain_result = player.process_daily_login()
        uow.track(player)

        box_xgen = 0
        box_fragments = 0
        box_items: list[dict] = []

        if (
            domain_result.got_box
            and self.loot_box_service
            and self.loot_box_repo
            and self.inventory_repo
        ):
            open_box_uc = OpenLootBoxUseCase(
                self.loot_box_service, self.loot_box_repo, self.inventory_repo
            )
            loot_result = await open_box_uc.execute(player, LootBoxType.DAILY_42, uow)
            box_xgen = loot_result.xgen_earned
            box_fragments = loot_result.fragments_earned
            box_items = loot_result.items_earned or []

        await self.player_repo.save(player)
        await uow.commit()

        return DailyLoginResponseDTO(
            earned_xp=domain_result.earned_xp,
            new_streak=domain_result.new_streak,
            got_box=domain_result.got_box,
            already_claimed=domain_result.already_claimed,
            box_opened=domain_result.got_box,
            box_xgen=box_xgen,
            box_fragments=box_fragments,
            box_items=box_items,
        )
