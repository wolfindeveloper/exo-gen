from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UpdateZoneDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    image_url: str | None = None
    fuel_cost: float | None = None
    optimism_risk: float | None = None
    duration_seconds: int | None = None
    loot_table: list[dict] | None = None


class UpdateItemDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    rarity: str | None = None
    effect: dict | None = None
    is_tradable: bool | None = None
    sell_price: int | None = None


class UpdateChapterDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    is_secret: bool | None = None
    reward_xgen: int | None = None
    reward_fragments: int | None = None


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


class UpdateShopItemDTO(BaseModel):
    price_xgen: int | None = None
    daily_limit: int | None = None
    stock_limit: int | None = None
    is_active: bool | None = None


class UpdateStarsPackageDTO(BaseModel):
    stars_amount: int | None = None
    xgen_reward: int | None = None
    is_active: bool | None = None


class LootBoxConfigResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    box_type: str
    name: str
    description: str
    entries: list[dict]
    is_active: bool
