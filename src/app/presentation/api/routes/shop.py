from fastapi import APIRouter, Depends, HTTPException, Request

from app.infrastructure.security.rate_limiter import limiter
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService
from app.application.dtos.shop_dto import ShopItemResponseDTO, PurchaseItemDTO, PurchaseItemResponseDTO
from app.application.dtos.stars_dto import StarsPackageResponseDTO, BuyXgenRequestDTO, BuyXgenResponseDTO
from app.application.use_cases.get_shop_items import GetShopItemsUseCase
from app.application.use_cases.purchase_shop_item import PurchaseShopItemUseCase
from app.application.use_cases.get_stars_packages import GetStarsPackagesUseCase
from app.application.use_cases.buy_xgen import BuyXgenUseCase
from app.domain.entities.player import Player
from app.domain.exceptions import DomainError
from app.domain.exceptions.player import InsufficientXgenError
from app.domain.exceptions.stars import StarsPackageNotFoundError
from app.domain.uow import UnitOfWork
from app.domain.repositories.shop_repository import ShopItemRepository, PurchaseHistoryRepository
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.stars_repository import StarsPackageRepository
from app.domain.services.loot_box_service import LootBoxService
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import (
    get_shop_item_repo,
    get_purchase_history_repo,
    get_player_repo,
    get_item_repo,
    get_inventory_repo,
    get_loot_box_repo,
    get_stars_package_repo,
    get_uow,
)

router = APIRouter(prefix="/shop", tags=["Shop"])


@router.get("/", response_model=list[ShopItemResponseDTO])
@limiter.limit("30/minute")
async def get_shop_items(
    request: Request,
    shop_item_repo: ShopItemRepository = Depends(get_shop_item_repo),
):
    use_case = GetShopItemsUseCase(shop_item_repo=shop_item_repo)
    return await use_case.execute()


@router.post("/purchase", response_model=PurchaseItemResponseDTO)
@limiter.limit("10/minute")
async def purchase_item(
    request: Request,
    dto: PurchaseItemDTO,
    current_player: Player = Depends(get_current_player),
    shop_item_repo: ShopItemRepository = Depends(get_shop_item_repo),
    purchase_history_repo: PurchaseHistoryRepository = Depends(get_purchase_history_repo),
    player_repo: PlayerRepository = Depends(get_player_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = PurchaseShopItemUseCase(
        shop_item_repo=shop_item_repo,
        purchase_history_repo=purchase_history_repo,
        player_repo=player_repo,
        item_repo=item_repo,
        inventory_repo=inventory_repo,
        loot_box_repo=loot_box_repo,
        loot_box_service=LootBoxService(),
    )
    try:
        return await use_case.execute(current_player, dto, uow)
    except InsufficientXgenError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "insufficient_xgen",
                "message": str(e),
                "required": e.required,
                "available": e.available,
                "hint": "You can buy XGen with Stars",
            },
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stars-packages", response_model=list[StarsPackageResponseDTO])
@limiter.limit("30/minute")
async def get_stars_packages(
    request: Request,
    stars_package_repo: StarsPackageRepository = Depends(get_stars_package_repo),
):
    use_case = GetStarsPackagesUseCase(stars_package_repo=stars_package_repo)
    return await use_case.execute()


@router.post("/buy-xgen", response_model=BuyXgenResponseDTO)
@limiter.limit("10/minute")
async def buy_xgen(
    request: Request,
    dto: BuyXgenRequestDTO,
    current_player: Player = Depends(get_current_player),
    stars_package_repo: StarsPackageRepository = Depends(get_stars_package_repo),
):
    use_case = BuyXgenUseCase(
        stars_package_repo=stars_package_repo,
        telegram_bot_service=TelegramBotService(),
    )
    try:
        return await use_case.execute(current_player, dto)
    except StarsPackageNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
