from uuid import UUID

from app.domain.entities.player import Player
from app.domain.entities.ship import Ship
from app.domain.value_objects.resources import (
    TeaLevel,
    Optimism,
    XgenBalance,
    FragmentsBalance,
)
from app.domain.value_objects.equipment import SlotType
from app.domain.entities.zone import Zone
from app.domain.entities.expedition import Expedition, ExpeditionStatus
from app.domain.entities.article import Article
from app.domain.entities.chapter import Chapter
from app.domain.entities.season import Season
from app.domain.entities.item import Item, ItemType
from app.domain.entities.inventory_item import InventoryItem
from app.domain.entities.inventory import Inventory
from app.domain.entities.equipment import Equipment, EquippedArtifact
from app.domain.entities.loot_box_config import LootBoxConfig
from app.domain.value_objects.loot_box import LootBoxType, LootBoxEntry
from app.domain.entities.stars_package import StarsPackage
from app.domain.entities.transaction import Transaction, TransactionStatus
from app.domain.entities.player_settings import PlayerSettings
from app.infrastructure.persistence.models.loot_box_config_orm import LootBoxConfigORM
from app.infrastructure.persistence.models.player_orm import PlayerORM
from app.infrastructure.persistence.models.ship_orm import ShipORM
from app.infrastructure.persistence.models.zone_orm import ZoneORM
from app.infrastructure.persistence.models.expedition_orm import ExpeditionORM
from app.infrastructure.persistence.models.article_orm import ArticleORM
from app.infrastructure.persistence.models.chapter_orm import ChapterORM
from app.infrastructure.persistence.models.season_orm import SeasonORM
from app.infrastructure.persistence.models.item_orm import ItemORM
from app.infrastructure.persistence.models.inventory_item_orm import InventoryItemORM
from app.infrastructure.persistence.models.equipment_orm import EquipmentORM
from app.infrastructure.persistence.models.stars_package_orm import StarsPackageORM
from app.infrastructure.persistence.models.transaction_orm import TransactionORM
from app.infrastructure.persistence.models.player_settings_orm import PlayerSettingsORM
from app.domain.entities.shop import ShopItem, PurchaseHistory
from app.infrastructure.persistence.models.shop_orm import ShopItemORM, PurchaseHistoryORM


class PlayerMapper:
    @staticmethod
    def ship_to_orm(ship: Ship, player_id: UUID) -> ShipORM:
        return ShipORM(
            id=ship.id,
            player_id=player_id,
            name=ship.name,
            tea_level=ship.tea_level.value,
            optimism=ship.optimism.value,
            speed=ship.speed,
            defense=ship.defense,
            luck=ship.luck,
        )

    @staticmethod
    def ship_to_domain(ship_orm: ShipORM) -> Ship:
        equipment = None
        if hasattr(ship_orm, "equipment") and ship_orm.equipment is not None:
            equipment = EquipmentMapper.to_domain(ship_orm.equipment)

        return Ship(
            id=ship_orm.id,
            player_id=ship_orm.player_id,
            name=ship_orm.name,
            tea_level=TeaLevel(ship_orm.tea_level),
            optimism=Optimism(ship_orm.optimism),
            speed=ship_orm.speed,
            defense=ship_orm.defense,
            luck=ship_orm.luck,
            equipment=equipment,
        )

    @classmethod
    def player_to_orm(cls, player: Player) -> PlayerORM:
        return PlayerORM(
            id=player.id,
            telegram_id=player.telegram_id,
            username=player.username,
            xp=player.xp,
            xgen_balance=player.xgen_balance.value,
            fragments_balance=player.fragments_balance.value,
            daily_streak=player.daily_streak,
            last_login_date=player.last_login_date,
            total_expeditions=player.total_expeditions,
            total_artifacts_found=player.total_artifacts_found,
            deleted_at=player.deleted_at,
            ships=[cls.ship_to_orm(ship, player_id=player.id) for ship in player.ships],
        )

    @classmethod
    def player_to_domain(cls, player_orm: PlayerORM) -> Player:
        return Player(
            id=player_orm.id,
            telegram_id=player_orm.telegram_id,
            username=player_orm.username,
            xp=player_orm.xp,
            xgen_balance=XgenBalance(player_orm.xgen_balance),
            fragments_balance=FragmentsBalance(player_orm.fragments_balance),
            daily_streak=player_orm.daily_streak,
            last_login_date=player_orm.last_login_date,
            total_expeditions=player_orm.total_expeditions,
            total_artifacts_found=player_orm.total_artifacts_found,
            deleted_at=player_orm.deleted_at,
            ships=[cls.ship_to_domain(ship) for ship in player_orm.ships],
        )


class ZoneMapper:
    @staticmethod
    def zone_to_orm(zone: Zone) -> ZoneORM:
        return ZoneORM(
            id=zone.id,
            name=zone.name,
            description=zone.description,
            image_url=zone.image_url,
            fuel_cost=zone.fuel_cost,
            optimism_risk=zone.optimism_risk,
            duration_seconds=zone.duration_seconds,
            loot_table=zone.loot_table,
            deleted_at=zone.deleted_at,
        )

    @staticmethod
    def zone_to_domain(zone_orm: ZoneORM) -> Zone:
        return Zone(
            id=zone_orm.id,
            name=zone_orm.name,
            description=zone_orm.description,
            image_url=zone_orm.image_url,
            fuel_cost=zone_orm.fuel_cost,
            optimism_risk=zone_orm.optimism_risk,
            duration_seconds=zone_orm.duration_seconds,
            loot_table=zone_orm.loot_table,
            deleted_at=zone_orm.deleted_at,
        )


class ExpeditionMapper:
    @staticmethod
    def expedition_to_orm(expedition: Expedition) -> ExpeditionORM:
        return ExpeditionORM(
            id=expedition.id,
            ship_id=expedition.ship_id,
            zone_id=expedition.zone_id,
            started_at=expedition.started_at,
            ends_at=expedition.ends_at,
            status=expedition.status.value,
        )

    @staticmethod
    def expedition_to_domain(expedition_orm: ExpeditionORM) -> Expedition:
        return Expedition(
            id=expedition_orm.id,
            ship_id=expedition_orm.ship_id,
            zone_id=expedition_orm.zone_id,
            started_at=expedition_orm.started_at,
            ends_at=expedition_orm.ends_at,
            status=ExpeditionStatus(expedition_orm.status),
        )


class SeasonMapper:
    @staticmethod
    def season_to_domain(season_orm: SeasonORM) -> Season:
        return Season(
            id=season_orm.id,
            name=season_orm.name,
            description=season_orm.description,
            start_date=season_orm.start_date,
            end_date=season_orm.end_date,
            reward_xgen=season_orm.reward_xgen,
            reward_fragments=season_orm.reward_fragments,
            is_active=season_orm.is_active,
            deleted_at=season_orm.deleted_at,
        )

    @staticmethod
    def season_to_orm(season: Season) -> SeasonORM:
        return SeasonORM(
            id=season.id,
            name=season.name,
            description=season.description,
            start_date=season.start_date,
            end_date=season.end_date,
            reward_xgen=season.reward_xgen,
            reward_fragments=season.reward_fragments,
            is_active=season.is_active,
            deleted_at=season.deleted_at,
        )


class ArticleMapper:
    @staticmethod
    def article_to_domain(article_orm: ArticleORM) -> Article:
        return Article(
            id=article_orm.id,
            chapter_id=article_orm.chapter_id,
            title=article_orm.title,
            content=article_orm.content,
            fragment_cost=article_orm.fragment_cost,
            trigger_event_type=article_orm.trigger_event_type,
            required_item_id=article_orm.required_item_id,
            trigger_threshold=article_orm.trigger_threshold,
            deleted_at=article_orm.deleted_at,
        )

    @staticmethod
    def article_to_orm(article: Article) -> ArticleORM:
        return ArticleORM(
            id=article.id,
            chapter_id=article.chapter_id,
            title=article.title,
            content=article.content,
            fragment_cost=article.fragment_cost,
            trigger_event_type=article.trigger_event_type,
            required_item_id=article.required_item_id,
            trigger_threshold=article.trigger_threshold,
            deleted_at=article.deleted_at,
        )


class ChapterMapper:
    @classmethod
    def chapter_to_domain(cls, chapter_orm: ChapterORM) -> Chapter:
        articles = [ArticleMapper.article_to_domain(a) for a in chapter_orm.articles]

        return Chapter(
            id=chapter_orm.id,
            name=chapter_orm.name,
            description=chapter_orm.description,
            is_secret=chapter_orm.is_secret,
            season_id=chapter_orm.season_id,
            reward_xgen=chapter_orm.reward_xgen,
            reward_fragments=chapter_orm.reward_fragments,
            articles=articles,
            deleted_at=chapter_orm.deleted_at,
        )

    @classmethod
    def chapter_to_orm(cls, chapter: Chapter) -> ChapterORM:
        articles = [ArticleMapper.article_to_orm(a) for a in chapter.articles]

        return ChapterORM(
            id=chapter.id,
            name=chapter.name,
            description=chapter.description,
            is_secret=chapter.is_secret,
            season_id=chapter.season_id,
            reward_xgen=chapter.reward_xgen,
            reward_fragments=chapter.reward_fragments,
            articles=articles,
            deleted_at=chapter.deleted_at,
        )


class ItemMapper:
    @staticmethod
    def to_domain(orm: ItemORM) -> Item:
        return Item(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            type=ItemType(orm.type),
            rarity=orm.rarity,
            effect=orm.effect,
            is_tradable=orm.is_tradable,
            sell_price=orm.sell_price,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def to_orm(domain: Item) -> ItemORM:
        return ItemORM(
            id=domain.id,
            name=domain.name,
            description=domain.description,
            type=domain.type.value,
            rarity=domain.rarity,
            effect=domain.effect,
            is_tradable=domain.is_tradable,
            sell_price=domain.sell_price,
            deleted_at=domain.deleted_at,
        )


class InventoryItemMapper:
    @staticmethod
    def to_domain(orm: InventoryItemORM) -> InventoryItem:
        return InventoryItem(
            id=orm.id,
            player_id=orm.player_id,
            item_id=orm.item_id,
            quantity=orm.quantity,
            metadata=orm.item_metadata,  # Читаем из item_metadata, пишем в metadata
        )

    @staticmethod
    def to_orm(domain: InventoryItem) -> InventoryItemORM:
        return InventoryItemORM(
            id=domain.id,
            player_id=domain.player_id,
            item_id=domain.item_id,
            quantity=domain.quantity,
            item_metadata=domain.metadata,  # Читаем из metadata, пишем в item_metadata
        )


class EquipmentMapper:
    @staticmethod
    def to_domain(orm: EquipmentORM) -> Equipment:
        artifacts = [
            EquippedArtifact(
                item_id=UUID(a["item_id"]),
                slot_type=SlotType(a["slot_type"]),
                bonuses=a["bonuses"],
            )
            for a in orm.artifacts
        ]
        return Equipment(ship_id=orm.ship_id, artifacts=artifacts)

    @staticmethod
    def to_orm(domain: Equipment) -> EquipmentORM:
        return EquipmentORM(
            id=domain.id,
            ship_id=domain.ship_id,
            artifacts=[
                {
                    "item_id": str(a.item_id),
                    "slot_type": a.slot_type.value,
                    "bonuses": a.bonuses,
                }
                for a in domain.artifacts
            ],
        )


class InventoryMapper:
    @classmethod
    def to_domain(cls, player_id: UUID, items_orm: list[InventoryItemORM]) -> Inventory:
        """Собирает Агрегат Инвентаря из списка ORM-записей"""
        return Inventory(
            player_id=player_id,
            items=[InventoryItemMapper.to_domain(i) for i in items_orm],
        )


class LootBoxMapper:
    @staticmethod
    def to_domain(orm: LootBoxConfigORM) -> LootBoxConfig:
        entries = [
            LootBoxEntry(
                item_type=e["item_type"],
                amount=e["amount"],
                chance=e["chance"],
                item_id=UUID(e["item_id"]) if e.get("item_id") else None,
            )
            for e in orm.entries
        ]
        return LootBoxConfig(
            id=orm.id,
            box_type=LootBoxType(orm.box_type),
            name=orm.name,
            description=orm.description,
            entries=entries,
            is_active=orm.is_active,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def to_orm(domain: LootBoxConfig) -> LootBoxConfigORM:
        entries = [
            {
                "item_type": e.item_type,
                "amount": e.amount,
                "chance": e.chance,
                "item_id": str(e.item_id) if e.item_id else None,
            }
            for e in domain.entries
        ]
        return LootBoxConfigORM(
            id=domain.id,
            box_type=domain.box_type.value,
            name=domain.name,
            description=domain.description,
            entries=entries,
            is_active=domain.is_active,
            deleted_at=domain.deleted_at,
        )


class ShopItemMapper:
    @staticmethod
    def to_domain(orm: ShopItemORM) -> ShopItem:
        return ShopItem(
            id=orm.id,
            item_id=orm.item_id,
            price_xgen=orm.price_xgen,
            daily_limit=orm.daily_limit,
            stock_limit=orm.stock_limit,
            is_active=orm.is_active,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def to_orm(domain: ShopItem) -> ShopItemORM:
        return ShopItemORM(
            id=domain.id,
            item_id=domain.item_id,
            price_xgen=domain.price_xgen,
            daily_limit=domain.daily_limit,
            stock_limit=domain.stock_limit,
            is_active=domain.is_active,
            deleted_at=domain.deleted_at,
        )


class PurchaseHistoryMapper:
    @staticmethod
    def to_domain(orm: PurchaseHistoryORM) -> PurchaseHistory:
        return PurchaseHistory(
            id=orm.id,
            player_id=orm.player_id,
            shop_item_id=orm.shop_item_id,
            purchased_at=orm.purchased_at,
        )

    @staticmethod
    def to_orm(domain: PurchaseHistory) -> PurchaseHistoryORM:
        return PurchaseHistoryORM(
            id=domain.id,
            player_id=domain.player_id,
            shop_item_id=domain.shop_item_id,
            purchased_at=domain.purchased_at,
        )


class StarsPackageMapper:
    @staticmethod
    def to_domain(orm: StarsPackageORM) -> StarsPackage:
        return StarsPackage(
            id=orm.id,
            stars_amount=orm.stars_amount,
            xgen_reward=orm.xgen_reward,
            is_active=orm.is_active,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def to_orm(domain: StarsPackage) -> StarsPackageORM:
        return StarsPackageORM(
            id=domain.id,
            stars_amount=domain.stars_amount,
            xgen_reward=domain.xgen_reward,
            is_active=domain.is_active,
            deleted_at=domain.deleted_at,
        )


class PlayerSettingsMapper:
    @staticmethod
    def to_domain(orm: PlayerSettingsORM) -> PlayerSettings:
        return PlayerSettings(
            player_id=orm.player_id,
            language=orm.language,
            music_enabled=orm.music_enabled,
        )

    @staticmethod
    def to_orm(domain: PlayerSettings) -> PlayerSettingsORM:
        return PlayerSettingsORM(
            player_id=domain.player_id,
            language=domain.language,
            music_enabled=domain.music_enabled,
        )


class TransactionMapper:
    @staticmethod
    def to_domain(orm: TransactionORM) -> Transaction:
        return Transaction(
            id=orm.id,
            player_id=orm.player_id,
            telegram_charge_id=orm.telegram_charge_id,
            stars_amount=orm.stars_amount,
            xgen_amount=orm.xgen_amount,
            status=TransactionStatus(orm.status),
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(domain: Transaction) -> TransactionORM:
        return TransactionORM(
            id=domain.id,
            player_id=domain.player_id,
            telegram_charge_id=domain.telegram_charge_id,
            stars_amount=domain.stars_amount,
            xgen_amount=domain.xgen_amount,
            status=domain.status.value,
            created_at=domain.created_at,
        )
