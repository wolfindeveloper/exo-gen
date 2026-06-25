import uuid

from app.domain.entities.player import Player
from app.domain.entities.ship import Ship
from app.domain.repositories.player_repository import PlayerRepository
from app.application.dtos.player_dto import CreatePlayerDTO

class CreatePlayerUseCase():
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo


    async def execute(self, dto: CreatePlayerDTO) -> Player:
        player = await self.player_repo.get_by_telegram_id(telegram_id=dto.telegram_id)

        if not player:
            player = Player(
                id=uuid.uuid4(),
                telegram_id=dto.telegram_id,
                username=dto.username,
            )

            new_ship = Ship(
                id=uuid.uuid4(),
                player_id=player.id
            )

            player.ships.append(new_ship)

            await self.player_repo.save(player)

        return player

        