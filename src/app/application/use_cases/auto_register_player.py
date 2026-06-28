import uuid
from datetime import datetime, timezone

from app.domain.entities.player import Player
from app.domain.entities.ship import Ship
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.events.player_events import PlayerRegisteredEvent


class AutoRegisterPlayerUseCase:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    async def execute(self, telegram_id: int, username: str, uow: UnitOfWork) -> Player:
        player = await self.player_repo.get_by_telegram_id(telegram_id)

        if player:
            return player

        player_id = uuid.uuid4()
        player = Player(
            id=player_id,
            telegram_id=telegram_id,
            username=username,
            xp=0,
            daily_streak=0,
            xgen_balance=100,
            fragments_balance=50,
            ships=[Ship(id=uuid.uuid4(), player_id=player_id)]
        )
        player.register_event(PlayerRegisteredEvent(
            occurred_at=datetime.now(timezone.utc),
            player_id=player_id,
            telegram_id=telegram_id
        ))
        uow.track(player)
        await self.player_repo.save(player)
        await uow.commit()

        return player
