import uuid

from app.domain.entities.player import Player
from app.domain.entities.ship import Ship
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository


class CreatePlayerUseCase:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    async def execute(self, telegram_id: int, username: str, uow: UnitOfWork) -> Player:
        player = await self.player_repo.get_by_telegram_id(telegram_id=telegram_id)

        if not player:
            player = Player(
                id=uuid.uuid4(),
                telegram_id=telegram_id,
                username=username,
            )

            new_ship = Ship(
                id=uuid.uuid4(),
                player_id=player.id
            )

            player.ships.append(new_ship)

            await self.player_repo.save(player)
            await uow.commit()

        return player

        