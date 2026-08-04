from fastapi import Depends

from app.presentation.api.dependencies import (
    get_player_repo,
    get_inventory_repo,
    get_loot_box_repo,
    get_item_repo,
    get_player_settings_repo,
    get_uow,
    require_telegram_user,
)
from app.infrastructure.security.telegram_auth import TelegramUserDTO
from app.application.use_cases.auto_register_player import AutoRegisterPlayerUseCase
from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.player_settings_repository import PlayerSettingsRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.services.loot_box_service import LootBoxService


async def get_current_player(
    telegram_user: TelegramUserDTO = Depends(require_telegram_user),
    player_repo: PlayerRepository = Depends(get_player_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    settings_repo: PlayerSettingsRepository = Depends(get_player_settings_repo),
    uow: UnitOfWork = Depends(get_uow),
) -> Player:
    telegram_id = telegram_user.telegram_id
    username = (
        telegram_user.username
        or telegram_user.first_name
        or f"user_{telegram_id}"
    )

    player = await player_repo.get_by_telegram_id(telegram_id)
    if not player:
        use_case = AutoRegisterPlayerUseCase(
            player_repo,
            loot_box_service=LootBoxService(),
            loot_box_repo=loot_box_repo,
            inventory_repo=inventory_repo,
            item_repo=item_repo,
            settings_repo=settings_repo,
        )
        player = await use_case.execute(telegram_id, username, uow)

    return player
