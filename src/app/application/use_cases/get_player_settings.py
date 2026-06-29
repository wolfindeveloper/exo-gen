from uuid import UUID

from app.domain.repositories.player_settings_repository import PlayerSettingsRepository
from app.application.dtos.player_settings_dto import PlayerSettingsDTO


class GetPlayerSettingsUseCase:
    def __init__(self, settings_repo: PlayerSettingsRepository):
        self.settings_repo = settings_repo

    async def execute(self, player_id: UUID) -> PlayerSettingsDTO:
        settings = await self.settings_repo.get_by_player_id(player_id)
        if not settings:
            return PlayerSettingsDTO(language="en", music_enabled=True)
        return PlayerSettingsDTO(
            language=settings.language,
            music_enabled=settings.music_enabled,
        )
