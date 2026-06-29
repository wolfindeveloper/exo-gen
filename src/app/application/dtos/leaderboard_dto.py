from pydantic import BaseModel


class PlayerShortStatsDTO(BaseModel):
    rank: int
    username: str | None
    xp: int
    level: int


class GlobalLeaderboardDTO(BaseModel):
    my_rank: int
    top_players: list[PlayerShortStatsDTO]
