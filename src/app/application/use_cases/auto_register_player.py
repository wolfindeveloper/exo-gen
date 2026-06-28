import uuid
from datetime import datetime, timezone

from app.domain.entities.player import Player
from app.domain.entities.ship import Ship
from app.domain.uow import UnitOfWork
from app.domain.value_objects.loot_box import LootBoxType
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService
from app.domain.events.player_events import PlayerRegisteredEvent
from app.application.use_cases.open_loot_box import OpenLootBoxUseCase


class AutoRegisterPlayerUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        loot_box_service: LootBoxService,
        loot_box_repo: LootBoxRepository,
        inventory_repo: InventoryRepository,
    ):
        self.player_repo = player_repo
        self.loot_box_service = loot_box_service
        self.loot_box_repo = loot_box_repo
        self.inventory_repo = inventory_repo

    async def execute(self, telegram_id: int, username: str, uow: UnitOfWork) -> Player:
        player = await self.player_repo.get_by_telegram_id(telegram_id)

        if player:
            return player

        player_id = uuid.uuid4()
        player = Player(
            id=player_id,
            telegram_id=telegram_id,
            username=username,
            xp=0,
            daily_streak=0,
            xgen_balance=100,
            fragments_balance=50,
            ships=[Ship(id=uuid.uuid4(), player_id=player_id)],
        )
        player.register_event(
            PlayerRegisteredEvent(
                occurred_at=datetime.now(timezone.utc),
                player_id=player_id,
                telegram_id=telegram_id,
            )
        )
        uow.track(player)
        await self.player_repo.save(player)

        open_box_uc = OpenLootBoxUseCase(
            self.loot_box_service,
            self.loot_box_repo,
            self.inventory_repo,
        )
        _ = await open_box_uc.execute(player, LootBoxType.WELCOME, uow)
        await self.player_repo.save(player)

        await uow.commit()

        return player
