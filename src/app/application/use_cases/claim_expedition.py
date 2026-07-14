from uuid import UUID
from datetime import datetime, timezone

from app.domain.entities.player import Player
from app.domain.entities.item import ItemType
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.entities.expedition import ExpeditionStatus
from app.domain.exceptions.expedition import ExpeditionNotFoundError, ExpeditionNotFinishedError, ExpeditionAlreadyClaimedError
from app.domain.exceptions.player import PlayerNotFoundError
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.exceptions.zone import ZoneNotFoundError

from app.application.dtos.claim_expedition_dto import (
    ClaimExpeditionDTO,
    ClaimExpeditionResponseDTO,
    ClaimedItemDTO
)
from app.domain.services.loot_generator import generate_loot


class ClaimExpeditionUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        zone_repo: ZoneRepository,
        expedition_repo: ExpeditionRepository,
        inventory_repo: InventoryRepository,
        item_repo: ItemRepository,
    ):
        self.player_repo = player_repo
        self.zone_repo = zone_repo
        self.expedition_repo = expedition_repo
        self.inventory_repo = inventory_repo
        self.item_repo = item_repo

    async def execute(self, player: Player, dto: ClaimExpeditionDTO, uow: UnitOfWork) -> ClaimExpeditionResponseDTO:
        expedition = await self.expedition_repo.get_by_id(dto.expedition_id, for_update=True)
        if not expedition:
            raise ExpeditionNotFoundError(f"Expedition {dto.expedition_id} not found")

        if expedition.status == ExpeditionStatus.COMPLETED:
            raise ExpeditionAlreadyClaimedError("Loot already claimed")

        player = await self.player_repo.get_by_id_for_update(player.id)
        if not player:
            raise PlayerNotFoundError(f"Player {player.id} not found")

        ship = next((s for s in player.ships if s.id == expedition.ship_id), None)
        if not ship:
            raise ShipNotFoundError("Expedition does not belong to player's ship")

        now = datetime.now(timezone.utc)
        if now < expedition.ends_at:
            raise ExpeditionNotFinishedError("Expedition is not finished yet")

        zone = await self.zone_repo.get_by_id(expedition.zone_id)
        if not zone:
            raise ZoneNotFoundError(f"Zone {expedition.zone_id} not found")

        loot = generate_loot(zone.loot_table)

        player.add_xgen(loot["xgen"])
        player.add_fragments(loot["fragments"])

        # XP за экспедицию
        duration_hours = zone.duration_seconds / 3600
        risk_percent = zone.optimism_risk
        total_xp = int(20 * duration_hours + risk_percent * 2)
        player.xp += total_xp
        player.increment_expeditions()

        inventory = await self.inventory_repo.get_by_player_id(player.id, for_update=True)
        claimed_items_dtos = []

        loot_items = loot.get("items", [])
        if loot_items:
            item_ids = [UUID(d["item_id"]) for d in loot_items]
            items = await self.item_repo.get_by_ids(item_ids)
            item_type_map = {item.id: item.type for item in items}
            item_name_map = {item.id: item.name for item in items}
        else:
            item_type_map = {}
            item_name_map = {}

        for item_drop in loot_items:
            item_id = UUID(item_drop["item_id"])
            amount = item_drop["amount"]

            inventory.add_item(item_id=item_id, quantity=amount)
            if item_type_map.get(item_id) == ItemType.ARTIFACT:
                player.increment_artifacts_found(amount)

            claimed_items_dtos.append(ClaimedItemDTO(
                item_id=item_id,
                amount=amount,
                name=item_name_map.get(item_id),
            ))

        damage = max(0.0, zone.optimism_risk - ship.defense)
        ship.apply_expedition_wear_and_tear(zone.optimism_risk)

        expedition.complete(
            player_id=player.id,
            telegram_id=player.telegram_id,
            xgen_earned=loot["xgen"],
            fragments_earned=loot["fragments"],
            items_earned=loot.get("items", []),
        )

        uow.track(player, expedition)
        await self.player_repo.save(player)
        await self.expedition_repo.save(expedition)
        await self.inventory_repo.save(inventory)
        await uow.commit()

        return ClaimExpeditionResponseDTO(
            xgen_earned=loot["xgen"],
            fragments_earned=loot["fragments"],
            xp_earned=total_xp,
            items_earned=claimed_items_dtos,
            optimism_lost=damage,
            current_tea=ship.tea_level.value,
            current_optimism=ship.optimism.value
        )
