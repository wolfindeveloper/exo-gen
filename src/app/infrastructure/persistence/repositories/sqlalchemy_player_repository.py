from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

from app.domain.entities.player import Player
from app.infrastructure.persistence.models.player_orm import PlayerORM
from app.infrastructure.persistence.models.ship_orm import ShipORM
from app.domain.repositories.player_repository import PlayerRepository
from app.infrastructure.persistence.mappers import PlayerMapper

class SQLAlchemyPlayerRepository(PlayerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, player_id: UUID) -> Player | None:
        result = await self.session.execute(
            select(PlayerORM)
            .options(selectinload(PlayerORM.ships))
            .where(PlayerORM.id == player_id)
        )
        player_orm = result.scalar_one_or_none()
        if not player_orm:
            return None
        return PlayerMapper.player_to_domain(player_orm=player_orm)

    async def get_by_telegram_id(self, telegram_id: int) -> Player | None:
        result = await self.session.execute(
            select(PlayerORM)
            .options(
                selectinload(PlayerORM.ships).selectinload(ShipORM.equipment)
            )
            .where(PlayerORM.telegram_id == telegram_id)
            .with_for_update()
        )

        player_orm = result.scalar_one_or_none()

        if not player_orm:
            return None

        return PlayerMapper.player_to_domain(player_orm=player_orm)


    async def get_by_id_for_update(self, player_id: UUID) -> Player | None:
        result = await self.session.execute(
            select(PlayerORM)
            .options(
                selectinload(PlayerORM.ships).selectinload(ShipORM.equipment)
            )
            .where(PlayerORM.id == player_id)
            .with_for_update()
        )
        player_orm = result.scalar_one_or_none()
        if not player_orm:
            return None
        return PlayerMapper.player_to_domain(player_orm=player_orm)

    async def get_by_ship_id(self, ship_id: UUID) -> Player | None:
        result = await self.session.execute(
            select(PlayerORM)
            .options(
                selectinload(PlayerORM.ships).selectinload(ShipORM.equipment)
            )
            .join(PlayerORM.ships)
            .where(ShipORM.id == ship_id)
        )
        player_orm = result.scalar_one_or_none()
        if not player_orm:
            return None
        return PlayerMapper.player_to_domain(player_orm=player_orm)

    async def save(self, player: Player) -> None:
        player_orm = PlayerMapper.player_to_orm(player)
        await self.session.merge(player_orm)

    async def get_top_players_by_xp(self, limit: int = 100) -> list[tuple[str | None, int, UUID]]:
        result = await self.session.execute(
            select(PlayerORM.username, PlayerORM.xp, PlayerORM.id)
            .order_by(PlayerORM.xp.desc())
            .limit(limit)
        )
        return [(row.username, row.xp, row.id) for row in result.all()]

    async def get_player_rank_by_xp(self, player_id: UUID) -> int:
        player = await self.session.get(PlayerORM, player_id)
        if not player:
            return 0
        result = await self.session.execute(
            select(func.count())
            .select_from(PlayerORM)
            .where(PlayerORM.xp > player.xp)
        )
        return result.scalar_one() + 1