from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.player_settings import PlayerSettings
from app.domain.repositories.player_settings_repository import PlayerSettingsRepository
from app.infrastructure.persistence.models.player_settings_orm import PlayerSettingsORM
from app.infrastructure.persistence.mappers import PlayerSettingsMapper


class SQLAlchemyPlayerSettingsRepository(PlayerSettingsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_player_id(self, player_id: UUID) -> PlayerSettings | None:
        result = await self.session.execute(
            select(PlayerSettingsORM).where(PlayerSettingsORM.player_id == player_id)
        )
        orm = result.scalar_one_or_none()
        if not orm:
            return None
        return PlayerSettingsMapper.to_domain(orm)

    async def save(self, settings: PlayerSettings) -> None:
        orm = PlayerSettingsMapper.to_orm(settings)
        await self.session.merge(orm)
