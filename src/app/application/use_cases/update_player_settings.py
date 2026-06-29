from uuid import UUID

from app.domain.repositories.player_settings_repository import PlayerSettingsRepository
from app.domain.entities.player_settings import PlayerSettings
from app.application.dtos.player_settings_dto import (
    UpdatePlayerSettingsDTO,
    PlayerSettingsDTO,
)


class UpdatePlayerSettingsUseCase:
    def __init__(self, settings_repo: PlayerSettingsRepository):
        self.settings_repo = settings_repo

    async def execute(
        self, player_id: UUID, dto: UpdatePlayerSettingsDTO
    ) -> PlayerSettingsDTO:
        settings = await self.settings_repo.get_by_player_id(player_id)
        if not settings:
            settings = PlayerSettings(player_id=player_id)

        if dto.language is not None:
            settings.language = dto.language
        if dto.music_enabled is not None:
            settings.music_enabled = dto.music_enabled

        await self.settings_repo.save(settings)

        return PlayerSettingsDTO(
            language=settings.language,
            music_enabled=settings.music_enabled,
        )
