from datetime import datetime
from typing import Generic, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator, validator

T = TypeVar("T")


# --- Валидаторы эффектов ---
class ConsumableEffectDTO(BaseModel):
    restore_tea: int | None = None
    restore_optimism: int | None = None


class ArtifactEffectDTO(BaseModel):
    bonus_speed: float | None = None
    bonus_defense: float | None = None
    bonus_capacity: float | None = None
    bonus_luck: float | None = None
    bonus_fuel: float | None = None
    bonus_repair: float | None = None
    bonus_xp: float | None = None
    bonus_fragment: float | None = None


# --- Валидаторы лута ---
class LootDropEntryDTO(BaseModel):
    drop_type: Literal["xgen", "fragments", "item"]
    amount: int = Field(gt=0)
    chance: float = Field(ge=0.0, le=1.0)
    item_id: UUID | None = None

    @validator('item_id', always=True)
    def check_item_id(cls, v, values):
        if values.get('drop_type') == 'item' and v is None:
            raise ValueError("item_id required for drop_type 'item'")
        return v


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)
    search: str | None = None
    sort_by: str | None = None
    sort_order: Literal["asc", "desc"] = "desc"


class PaginatedResponseDTO(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ItemEffectValidator(RootModel[ConsumableEffectDTO | ArtifactEffectDTO]):
    @field_validator("root", mode="after")
    @classmethod
    def validate_effect(cls, v: ConsumableEffectDTO | ArtifactEffectDTO) -> ConsumableEffectDTO | ArtifactEffectDTO:
        if isinstance(v, ConsumableEffectDTO):
            if v.restore_tea is None and v.restore_optimism is None:
                raise ValueError("Consumable must have restore_tea or restore_optimism")
        if isinstance(v, ArtifactEffectDTO):
            if not any(
                [
                    v.bonus_speed,
                    v.bonus_defense,
                    v.bonus_capacity,
                    v.bonus_luck,
                    v.bonus_fuel,
                    v.bonus_repair,
                    v.bonus_xp,
                    v.bonus_fragment,
                ]
            ):
                raise ValueError("Artifact must have at least one bonus")
        return v


class LootDropEntry(BaseModel):
    drop_type: Literal["xgen", "fragments", "item"]
    amount: int = Field(gt=0)
    chance: float = Field(ge=0.0, le=1.0)
    item_id: UUID | None = None

    @model_validator(mode="after")
    def validate_item_id(self) -> "LootDropEntry":
        if self.drop_type == "item" and self.item_id is None:
            raise ValueError("item_id is required when drop_type is 'item'")
        if self.drop_type != "item" and self.item_id is not None:
            raise ValueError("item_id should be null for non-item drops")
        return self


class LootTableValidator(RootModel[list[LootDropEntry]]):
    @field_validator("root", mode="after")
    @classmethod
    def validate_loot_table(cls, v: list[LootDropEntry]) -> list[LootDropEntry]:
        if not v:
            raise ValueError("Loot table cannot be empty")
        return v


class UpdateZoneDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    image_url: str | None = None
    fuel_cost: float | None = None
    optimism_risk: float | None = None
    duration_seconds: int | None = None
    loot_table: list[LootDropEntryDTO] | None = None


class ChapterRewardItemDTO(BaseModel):
    item_id: UUID
    quantity: int = Field(gt=0)


class UpdateItemDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    rarity: str | None = None
    effect: ConsumableEffectDTO | ArtifactEffectDTO | None = None
    is_tradable: bool | None = None
    sell_price: int | None = None
    image_url: str | None = None


class UpdateChapterDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    is_secret: bool | None = None
    reward_xgen: int | None = None
    reward_fragments: int | None = None
    reward_items: list[ChapterRewardItemDTO] | None = None


class UpdateArticleDTO(BaseModel):
    title: str | None = None
    content: str | None = None
    fragment_cost: int | None = None
    trigger_event_type: str | None = None
    trigger_threshold: int | None = None
    required_item_id: UUID | None = None


class UpdateSeasonDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    reward_xgen: int | None = None
    reward_fragments: int | None = None
    is_active: bool | None = None


class UpdateLootBoxConfigDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    entries: list[dict] | None = None
    is_active: bool | None = None


class BundleItemDTO(BaseModel):
    item_id: UUID
    quantity: int = Field(gt=0)


class UpdateShopItemDTO(BaseModel):
    price_xgen: int | None = None
    daily_limit: int | None = None
    stock_limit: int | None = None
    is_active: bool | None = None
    bundle_items: list[BundleItemDTO] | None = None


class UpdateStarsPackageDTO(BaseModel):
    stars_amount: int | None = None
    xgen_reward: int | None = None
    is_active: bool | None = None


class CreateShopItemDTO(BaseModel):
    item_id: UUID | None = None
    price_xgen: int = Field(ge=0)
    daily_limit: int = Field(ge=0, default=0)
    stock_limit: int = Field(ge=0, default=0)
    is_active: bool = True
    bundle_items: list[BundleItemDTO] = []

    @model_validator(mode='after')
    def validate_bundle(self):
        if self.bundle_items and self.item_id:
            raise ValueError("Provide either item_id OR bundle_items, not both")
        if not self.bundle_items and not self.item_id:
            raise ValueError("Provide either item_id or bundle_items")
        return self


# --- Create DTOs (обязательные поля) ---
class CreateItemDTO(BaseModel):
    name: str
    description: str
    rarity: str
    effect: ConsumableEffectDTO | ArtifactEffectDTO
    is_tradable: bool
    sell_price: int


class CreateZoneDTO(BaseModel):
    name: str
    description: str
    image_url: str
    fuel_cost: float
    optimism_risk: float
    duration_seconds: int
    loot_table: list[LootDropEntryDTO]


class LootBoxConfigResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    box_type: str
    name: str
    description: str
    entries: list[dict]
    is_active: bool
