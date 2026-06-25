from dataclasses import dataclass, field
from uuid import UUID

from app.domain.entities.article import Article

@dataclass
class Chapter:
    id: UUID
    name: str
    description: str
    is_secret: bool # True - открывается триггерами, False - покупается за фрагменты
    season_id: UUID | None = None  # <-- Новое! Если None - постоянная глава
    reward_xgen: int = 0
    reward_fragments: int = 0
    articles: list["Article"] = field(default_factory=list)

    def is_seasonal(self) -> bool:
        return self.season_id is not None