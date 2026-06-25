from app.domain.repositories.player_repository import PlayerRepository
from app.application.dtos.player_response_dto import PlayerResponseDTO


class GetPlayerUseCase:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    
    async def execute(self, telegram_id: int) -> PlayerResponseDTO | None:
        player = await self.player_repo.get_by_telegram_id(telegram_id)

        if not player:
            return None

        ship = next((s for s in player.ships), None)

        return PlayerResponseDTO(
            id=player.id,
            telegram_id=player.telegram_id,
            username=player.username,
            xp=player.xp,
            xgen_balance=player.xgen_balance,
            fragments_balance=player.fragments_balance,
            daily_streak=player.daily_streak,
            ship_count=len(player.ships),
            ship_id=ship.id if ship else None
        )