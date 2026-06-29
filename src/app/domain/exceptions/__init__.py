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
)
from app.domain.exceptions.guide import (
    ArticleNotFoundError,
    ChapterNotFoundError,
    ArticleAlreadyUnlockedError,
    CannotBuySecretArticleError,
)
from app.domain.exceptions.zone import ZoneNotFoundError
from app.domain.exceptions.equipment import (
    EquipmentNotFoundError,
    ArtifactNotEquippedError,
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
    "ArticleNotFoundError",
    "ChapterNotFoundError",
    "ArticleAlreadyUnlockedError",
    "CannotBuySecretArticleError",
    "ZoneNotFoundError",
    "EquipmentNotFoundError",
    "ArtifactNotEquippedError",
]
