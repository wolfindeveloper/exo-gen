from uuid import UUID
from datetime import datetime, timezone

from app.domain.uow import UnitOfWork
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.entities.expedition import ExpeditionStatus


class ProcessFinishedExpeditionsUseCase:
    def __init__(
        self,
        expedition_repo: ExpeditionRepository,
        player_repo: PlayerRepository,
    ):
        self.expedition_repo = expedition_repo
        self.player_repo = player_repo

    async def execute(self, uow: UnitOfWork) -> int:
        expeditions = await self.expedition_repo.get_finished_expeditions()
        if not expeditions:
            return 0

        for expedition in expeditions:
            player = await self.player_repo.get_by_ship_id(expedition.ship_id)
            if not player:
                continue

            expedition.complete(
                player_id=player.id,
                telegram_id=player.telegram_id,
                xgen_earned=0,
                fragments_earned=0,
                items_earned=[],
                auto_finished=True,
            )

            uow.track(expedition)
            await self.expedition_repo.save(expedition)

        await uow.commit()
        return len(expeditions)