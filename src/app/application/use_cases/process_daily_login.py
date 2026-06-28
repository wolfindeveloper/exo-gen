from app.domain.exceptions.player import PlayerNotFoundError
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.application.dtos.daily_login_dto import DailyLoginResponseDTO


class ProcessDailyLoginUseCase:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    async def execute(self, telegram_id: int, uow: UnitOfWork) -> DailyLoginResponseDTO:
        player = await self.player_repo.get_by_telegram_id(telegram_id)

        if not player:
            raise PlayerNotFoundError(f"Player with telegram_id {telegram_id} not found")

        domain_result = player.process_daily_login()
        uow.track(player)
        await self.player_repo.save(player)
        await uow.commit()

        return DailyLoginResponseDTO(
            earned_xp=domain_result.earned_xp,
            new_streak=domain_result.new_streak,
            got_box=domain_result.got_box,
            already_claimed=domain_result.already_claimed
        )