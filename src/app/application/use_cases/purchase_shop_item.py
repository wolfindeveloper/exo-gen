from uuid import uuid4
from datetime import datetime, timezone

from app.application.dtos.shop_dto import PurchaseItemDTO, PurchaseItemResponseDTO
from app.domain.entities.player import Player
from app.domain.entities.item import ItemType
from app.domain.entities.shop import PurchaseHistory
from app.domain.uow import UnitOfWork
from app.domain.value_objects.loot_box import LootBoxType
from app.domain.repositories.shop_repository import ShopItemRepository, PurchaseHistoryRepository
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService
from app.domain.services.clock import SystemClock
from app.domain.exceptions.shop import ShopItemNotFoundError
from app.application.use_cases.open_loot_box import OpenLootBoxUseCase


class PurchaseShopItemUseCase:
    def __init__(
        self,
        shop_item_repo: ShopItemRepository,
        purchase_history_repo: PurchaseHistoryRepository,
        player_repo: PlayerRepository,
        item_repo: ItemRepository,
        inventory_repo: InventoryRepository,
        loot_box_repo: LootBoxRepository,
        loot_box_service: LootBoxService,
    ):
        self.shop_item_repo = shop_item_repo
        self.purchase_history_repo = purchase_history_repo
        self.player_repo = player_repo
        self.item_repo = item_repo
        self.inventory_repo = inventory_repo
        self.loot_box_repo = loot_box_repo
        self.loot_box_service = loot_box_service

    async def execute(
        self, player: Player, dto: PurchaseItemDTO, uow: UnitOfWork
    ) -> PurchaseItemResponseDTO:
        shop_item = await self.shop_item_repo.get_by_id(dto.shop_item_id)
        if not shop_item:
            raise ShopItemNotFoundError(dto.shop_item_id)

        clock = SystemClock()
        today = clock.today()

        purchase_count_today = await self.purchase_history_repo.get_purchase_count_today(
            player.id, shop_item.id, today
        )
        total_purchase_count = await self.purchase_history_repo.get_total_purchase_count(
            shop_item.id
        )

        shop_item.can_purchase(purchase_count_today, total_purchase_count)

        player.spend_xgen(shop_item.price_xgen)

        item = await self.item_repo.get_by_id(shop_item.item_id)
        if not item:
            raise ShopItemNotFoundError(dto.shop_item_id)

        quantity = 1
        if item.type == ItemType.LOOT_BOX:
            open_box_uc = OpenLootBoxUseCase(
                loot_box_service=self.loot_box_service,
                loot_box_repo=self.loot_box_repo,
                inventory_repo=self.inventory_repo,
            )
            await open_box_uc.execute(player, LootBoxType.SHOP, uow)
        else:
            inventory = await self.inventory_repo.get_by_player_id(player.id)
            inventory.add_item(item_id=item.id, quantity=quantity)
            await self.inventory_repo.save(inventory)

        purchase = PurchaseHistory(
            id=uuid4(),
            player_id=player.id,
            shop_item_id=shop_item.id,
            purchased_at=clock.now(),
        )
        await self.purchase_history_repo.save(purchase)
        await self.player_repo.save(player)
        await uow.commit()

        return PurchaseItemResponseDTO(
            success=True,
            message="Item purchased successfully",
            item_id=item.id,
            quantity=quantity,
            xgen_spent=shop_item.price_xgen,
        )
