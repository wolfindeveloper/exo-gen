from app.domain.exceptions.base import DomainError
from app.domain.exceptions.player import (
    PlayerNotFoundError,
    PlayerAlreadyExistsError,
    InsufficientFragmentsError,
    InsufficientXgenError,
    DailyLoginAlreadyClaimedError,
)
from app.domain.exceptions.ship import (
    ShipNotFoundError,
    InsufficientTeaError,
    ShipAlreadyInExpeditionError,
    ShipDestroyedError,
)
from app.domain.exceptions.expedition import (
    ExpeditionNotFoundError,
    ExpeditionNotFinishedError,
    ExpeditionAlreadyClaimedError,
)
from app.domain.exceptions.inventory import (
    ItemNotFoundError,
    ItemNotInInventoryError,
    ItemNotConsumableError,
    InsufficientItemQuantityError,
    NoSuitableConsumableError,
    ItemInUseError,
)
from app.domain.exceptions.guide import (
    ArticleNotFoundError,
    ChapterNotFoundError,
    ArticleAlreadyUnlockedError,
    CannotBuySecretArticleError,
    SeasonExpiredError,
    KeyItemRequiredError,
    SeasonActiveError,
    SeasonHasProgressError,
    ArticleHasUnlocksError,
)
from app.domain.exceptions.zone import ZoneNotFoundError, ZoneHasActiveExpeditionsError
from app.domain.exceptions.equipment import (
    EquipmentNotFoundError,
    ArtifactNotEquippedError,
)
from app.domain.exceptions.loot_box import (
    LootBoxConfigNotFoundError,
)
from app.domain.exceptions.shop import (
    ShopItemNotFoundError,
    ShopItemDailyLimitReachedError,
    ShopItemOutOfStockError,
)
from app.domain.exceptions.stars import (
    StarsPackageNotFoundError,
    TransactionAlreadyProcessedError,
)

__all__ = [
    "DomainError",
    "PlayerNotFoundError",
    "PlayerAlreadyExistsError",
    "InsufficientFragmentsError",
    "InsufficientXgenError",
    "DailyLoginAlreadyClaimedError",
    "ShipNotFoundError",
    "InsufficientTeaError",
    "ShipAlreadyInExpeditionError",
    "ShipDestroyedError",
    "ExpeditionNotFoundError",
    "ExpeditionNotFinishedError",
    "ExpeditionAlreadyClaimedError",
    "ItemNotFoundError",
    "ItemNotInInventoryError",
    "ItemNotConsumableError",
    "InsufficientItemQuantityError",
    "NoSuitableConsumableError",
    "ItemInUseError",
    "ArticleNotFoundError",
    "ChapterNotFoundError",
    "ArticleAlreadyUnlockedError",
    "CannotBuySecretArticleError",
    "SeasonExpiredError",
    "KeyItemRequiredError",
    "SeasonActiveError",
    "SeasonHasProgressError",
    "ArticleHasUnlocksError",
    "ZoneNotFoundError",
    "ZoneHasActiveExpeditionsError",
    "EquipmentNotFoundError",
    "ArtifactNotEquippedError",
    "ShopItemNotFoundError",
    "ShopItemDailyLimitReachedError",
    "ShopItemOutOfStockError",
    "StarsPackageNotFoundError",
    "TransactionAlreadyProcessedError",
]
