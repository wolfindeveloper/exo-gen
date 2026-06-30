from pydantic import BaseModel


class PlayerShortStatsDTO(BaseModel):
    rank: int
    username: str | None
    xp: int
    level: int


class MetricEntryDTO(BaseModel):
    rank: int
    username: str | None
    value: int


class MetricLeaderboardDTO(BaseModel):
    my_rank: int = 0
    top: list[MetricEntryDTO] = []


class GlobalLeaderboardDTO(BaseModel):
    my_rank: int
    top_players: list[PlayerShortStatsDTO]
    expeditions: MetricLeaderboardDTO = MetricLeaderboardDTO()
    artifacts: MetricLeaderboardDTO = MetricLeaderboardDTO()
    xgen: MetricLeaderboardDTO = MetricLeaderboardDTO()
    articles: MetricLeaderboardDTO = MetricLeaderboardDTO()
