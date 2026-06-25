from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.domain.entities.player import Player
from app.infrastructure.persistence.models.player_orm import PlayerORM
from app.domain.repositories.player_repository import PlayerRepository
from app.infrastructure.persistence.mappers import PlayerMapper

class SQLAlchemyPlayerRepository(PlayerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Player | None:
        result = await self.session.execute(
            select(PlayerORM)
            .options(selectinload(PlayerORM.ships))
            .where(PlayerORM.telegram_id == telegram_id)
        )

        player_orm = result.scalar_one_or_none()

        if not player_orm:
            return None

        return PlayerMapper.player_to_domain(player_orm=player_orm)


    async def save(self, player: Player) -> None:
        player_orm = PlayerMapper.player_to_orm(player)

        # 2. merge() умный: если объекта с таким ID нет в БД - он его создаст (INSERT).
        # Если есть - он обновит его поля (UPDATE).
        # Это избавляет нас от необходимости вручную писать if/else на проверку существования.
        merged_orm = await self.session.merge(player_orm)
        await self.session.commit()
        # 3. Обновляем состояние доменного объекта (например, если БД сгенерировала ID)
        # Но так как ID мы генерируем сами в Python, это опционально.
        await self.session.refresh(merged_orm)

        
        

        

        

        