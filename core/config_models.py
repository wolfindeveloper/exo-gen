"""Pydantic-модели для валидации игровых конфигов."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class LocalizedText(BaseModel):
    """Текст с локализацией RU/EN/LA."""

    ru: str = ""
    en: str = ""
    la: str = ""


class ShipConfig(BaseModel):
    """Модель корабля из config/ships.json."""

    name: LocalizedText
    description: LocalizedText
    image_path: str
    tier: int = Field(ge=1, le=5)
    slug: str
    is_nft: bool = False
    base_stability: int = Field(ge=0, le=100)
    expedition_slots: int = Field(ge=1, le=5)


class FuelConfig(BaseModel):
    """Модель топлива из config/fuels.json."""

    name: LocalizedText
    description: LocalizedText
    image_path: str
    tier: int = Field(ge=1, le=5)
    slug: str


class ExpeditionConfig(BaseModel):
    """Модель экспедиции из config/expeditions.json."""

    name: LocalizedText
    description: LocalizedText
    slug: str
    tier: int = Field(ge=1, le=5)
    duration_hours: int = Field(ge=1)
    xp_reward: int = Field(ge=0)
    fuel_required: list[str]
    loot_table: list[str]
    damage_chance_percent: int = Field(ge=0, le=100)
    requires_verification: str | None = None


class OverdriveMode(BaseModel):
    """Режим overdrive из config/overdrive.json."""

    slug: str
    loot_multiplier: float = Field(ge=1.0)
    time_reduction_percent: int = Field(ge=0, le=100)
    damage_chance_percent: int = Field(ge=0, le=100)
    extra_fuel_required: int = Field(ge=0)
    guaranteed_loot_percent: int = Field(ge=0, le=100)
    essence_drop_multiplier: float = Field(ge=1.0)
    requires_insurance: bool = False
    unlocks_tier_min: int | None = None


class OverdriveConfig(BaseModel):
    """Корневая модель overdrive.json."""

    stable: OverdriveMode
    push: OverdriveMode
    overdrive: OverdriveMode
    anti_farm_max_per_day: int = Field(ge=0, default=10)


class RepairCostEntry(BaseModel):
    """Запись стоимости ремонта из config/repair_costs.json."""

    slug: str
    resource_cost_multiplier: float = Field(ge=0, default=1.0)
    duration_hours: int = Field(ge=0, default=0)
    xgen_cost: int = Field(ge=0, default=0)
    instant: bool = False
    requires_artifact: str | None = None
    description: str | None = None


class CalibrationCost(BaseModel):
    """Стоимость калибровки артефакта."""

    xgen: int = Field(ge=0)
    resource_slug: str


class ArtifactErosionSection(BaseModel):
    """Секция эрозии артефактов."""

    default_cycles: int = Field(ge=1)
    floor_percent: int = Field(ge=0, le=100)
    calibration_cost: CalibrationCost


class StakingYieldSection(BaseModel):
    """Секция дохода от стейкинга."""

    global_pool_total: int = Field(ge=0)
    daily_cap_percent: float = Field(ge=0, le=100)
    activity_multiplier: dict[str, float]
    rarity_multipliers: dict[str, float]


class ArtifactErosionConfig(BaseModel):
    """Конфиг эрозии артефактов из config/artifact_erosion.json."""

    artifact_erosion: ArtifactErosionSection
    staking_yield: StakingYieldSection


class EssenceDropMode(BaseModel):
    """Режим дропа эссенций."""

    base_chance_percent: int = Field(ge=0, le=100)
    multiplier: float = Field(ge=1.0, default=1.0)
    t4_unlocked: bool = False
    t5_unlocked: bool = False


class AntiFarmConfig(BaseModel):
    """Конфиг анти-фарма."""

    max_essences_per_day: int = Field(ge=0)
    cooldown_reset_hours: int = Field(ge=1)


class EssenceDropSection(BaseModel):
    """Секция дропа эссенций."""

    stable: EssenceDropMode
    push: EssenceDropMode
    overdrive: EssenceDropMode
    anti_farm: AntiFarmConfig


class EssenceDropConfig(BaseModel):
    """Конфиг дропа эссенций из config/essence_drop.json."""

    essence_drop: EssenceDropSection


class LabRulesSection(BaseModel):
    """Секция правил лаборатории."""

    min_essences: int = Field(ge=2)
    max_essences: int = Field(ge=2)
    xgen_burn_percent: int = Field(ge=0, le=100)
    failure_return_percent: int = Field(ge=0, le=100)
    hash_algorithm: str = "sha256"


class EssenceTierEntry(BaseModel):
    """Запись тира эссенции."""

    tier: int = Field(ge=1, le=5)
    slug: str


class LabRulesConfig(BaseModel):
    """Конфиг правил лаборатории из config/lab_rules.json."""

    lab_rules: LabRulesSection
    essence_tiers: dict[str, EssenceTierEntry]


class GalaxyZoneEntry(BaseModel):
    """Запись зоны галактики из config/galaxy_zones.json."""

    name: LocalizedText
    description: LocalizedText
    slug: str
    tier: int = Field(ge=1, le=5)
    image_path: str
    lore: str | LocalizedText | None = None
    drop_table: list[str] = Field(default_factory=list)


class MarketplaceConfig(BaseModel):
    """Конфиг маркетплейса из config/marketplace.json."""

    marketplace_fee_percent: int = Field(ge=0, le=100)
    burn_percent_of_fee: int = Field(ge=0, le=100)
    ecosystem_percent_of_fee: int = Field(ge=0, le=100)
    royalty_percent: int = Field(ge=0, le=100)
    external_marketplace_url: str = ""
    internal_p2p_enabled: bool = False
    allowed_tiers_for_trade: list[int] = Field(default_factory=list)
    artifact_trade_enabled: bool = True


class FleetNftConfig(BaseModel):
    """Конфиг NFT флота."""

    min_tier: int = Field(ge=1, le=5)
    royalty_percent: int = Field(ge=0, le=100)
    standard: str = "TEP-62"


class ArtifactNftConfig(BaseModel):
    """Конфиг NFT артефактов."""

    unique_per_hash: bool = True
    royalty_percent: int = Field(ge=0, le=100)
    standard: str = "TEP-62"


class PilotSbtConfig(BaseModel):
    """Конфиг SBT пилота."""

    soulbound: bool = True
    transferable: bool = False
    standard: str = "TEP-62"


class NftMintingSection(BaseModel):
    """Секция минтинга NFT."""

    fleet_nft: FleetNftConfig
    artifact_nft: ArtifactNftConfig
    pilot_sbt: PilotSbtConfig


class NftMintingConfig(BaseModel):
    """Конфиг минтинга NFT из config/nft_minting.json."""

    nft_minting: NftMintingSection


class NotificationEntry(BaseModel):
    """Запись уведомления из config/notifications.json."""

    slug: str
    template: LocalizedText
    cooldown_seconds: int = Field(ge=0)


class NotificationsSection(BaseModel):
    """Секция уведомлений."""

    expedition_completed: NotificationEntry
    repair_completed: NotificationEntry
    lab_craft_result: NotificationEntry
    daily_reminder: NotificationEntry


class NotificationsConfig(BaseModel):
    """Конфиг уведомлений из config/notifications.json."""

    notifications: NotificationsSection


class SeasonRewards(BaseModel):
    """Награды сезона."""

    box_slug: str
    count: int = Field(ge=1)


class SeasonEntry(BaseModel):
    """Запись сезона из config/seasons.json."""

    name: LocalizedText
    slug: str
    start_date: str
    end_date: str
    duration_days: int = Field(ge=1)
    weights: dict[str, float]
    rewards: dict[str, SeasonRewards]


class SeasonsConfig(BaseModel):
    """Конфиг сезонов из config/seasons.json."""

    season_1: SeasonEntry


class ShopBoxEntry(BaseModel):
    """Запись магазина коробок из config/shop_boxes.json."""

    name: LocalizedText
    slug: str
    tier: int = Field(ge=1, le=5)
    xgen_cost: int = Field(ge=0)
    lock_days: int = Field(ge=0)
    drop_table: list[str]


class ShopBoxesConfig(BaseModel):
    """Конфиг магазинов коробок из config/shop_boxes.json."""

    shop_boxes: dict[str, ShopBoxEntry]


class PromotionQuestEntry(BaseModel):
    """Запись квеста восхождения из config/promotion_quests.json."""

    slug: str
    required_expeditions: int = Field(ge=1)
    required_xp: int = Field(ge=0)
    crate_slug: str


class PromotionQuestsConfig(BaseModel):
    """Конфиг квестов восхождения из config/promotion_quests.json."""

    promotion_quests: dict[str, PromotionQuestEntry]


class RankEntry(BaseModel):
    """Запись ранга из config/ranks.json."""

    name: LocalizedText
    slug: str
    min_level: int = Field(ge=1)
    max_level: int = Field(ge=1)


class ProgressionConfig(BaseModel):
    """Секция прогрессии."""

    max_level: int = Field(ge=1)
    xp_base: int = Field(ge=1)
    xp_exponent: float = Field(ge=1.0)


class RanksConfig(BaseModel):
    """Конфиг рангов из config/ranks.json."""

    ranks: dict[str, RankEntry]
    progression: ProgressionConfig


class AvatarEntry(BaseModel):
    """Запись аватара из config/avatars.json."""

    name: LocalizedText
    slug: str
    image_path: str
    tier: int = Field(ge=1, le=5)
    unlock_condition: str = "default"


class AvatarsConfig(BaseModel):
    """Конфиг аватаров из config/avatars.json."""

    avatars: dict[str, AvatarEntry]
