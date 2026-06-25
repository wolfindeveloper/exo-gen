from uuid import UUID
from datetime import datetime, timezone

from app.domain.entities.player import Player
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.domain.repositories.inventory_repository import InventoryRepository # <-- НОВОЕ
from app.domain.entities.expedition import ExpeditionStatus

from app.application.dtos.claim_expedition_dto import (
    ClaimExpeditionDTO, 
    ClaimExpeditionResponseDTO, 
    ClaimedItemDTO # <-- НОВОЕ
)
from app.domain.services.loot_generator import generate_loot

class ClaimExpeditionUseCase:
    def __init__(
        self, 
        player_repo: PlayerRepository, 
        zone_repo: ZoneRepository, 
        expedition_repo: ExpeditionRepository,
        inventory_repo: InventoryRepository # <-- НОВОЕ
    ):
        self.player_repo = player_repo
        self.zone_repo = zone_repo
        self.expedition_repo = expedition_repo
        self.inventory_repo = inventory_repo # <-- НОВОЕ

    async def execute(self, player: Player, dto: ClaimExpeditionDTO) -> ClaimExpeditionResponseDTO:
        expedition = await self.expedition_repo.get_by_id(dto.expedition_id)
        if not expedition:
            raise ValueError("Expedition not found")

        ship = next((s for s in player.ships if s.id == expedition.ship_id), None)
        if not ship:
            raise ValueError("Expedition does not belong to player's ship")

        if expedition.status == ExpeditionStatus.COMPLETED:
            raise ValueError("Loot already claimed")

        now = datetime.now(timezone.utc)
        if now < expedition.ends_at:
            raise ValueError("Expedition is not finished yet")

        zone = await self.zone_repo.get_by_id(expedition.zone_id)
        if not zone:
            raise ValueError("Zone not found")

        # 1. Генерация лута
        loot = generate_loot(zone.loot_table)
        
        # 2. Начисление валют
        player.xgen_balance += loot["xgen"]
        player.fragments_balance += loot["fragments"]

        # 3. Добавление предметов в инвентарь (НОВОЕ)
        inventory = await self.inventory_repo.get_by_player_id(player.id)
        claimed_items_dtos = []
        
        for item_drop in loot.get("items", []):
            item_id = UUID(item_drop["item_id"])
            amount = item_drop["amount"]
            
            # Используем доменный метод Агрегата Inventory
            inventory.add_item(item_id=item_id, quantity=amount)
            
            claimed_items_dtos.append(ClaimedItemDTO(item_id=item_id, amount=amount))

        # 4. Износ корабля
        damage = max(0.0, zone.optimism_risk - ship.defense)
        ship.apply_expedition_wear_and_tear(zone.optimism_risk)

        # 5. Завершение экспедиции
        expedition.status = ExpeditionStatus.COMPLETED

        # 6. Сохранение всех изменений
        await self.player_repo.save(player)
        await self.expedition_repo.save(expedition)
        await self.inventory_repo.save(inventory) # <-- НОВОЕ: Сохраняем рюкзак

        return ClaimExpeditionResponseDTO(
            xgen_earned=loot["xgen"],
            fragments_earned=loot["fragments"],
            items_earned=claimed_items_dtos, # <-- НОВОЕ
            optimism_lost=damage,
            current_tea=ship.tea_level,
            current_optimism=ship.optimism
        )