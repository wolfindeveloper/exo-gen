from dataclasses import dataclass, field
from uuid import UUID

from app.domain.entities.article import Article

@dataclass
class Chapter:
    id: UUID
    name: str
    description: str
    is_secret: bool
    season_id: UUID | None = None
    reward_xgen: int = 0
    reward_fragments: int = 0
    articles: list["Article"] = field(default_factory=list)

    def is_seasonal(self) -> bool:
        return self.season_id is not None

    def check_completion(self, unlocked_article_ids: set[UUID]) -> bool:
        if self.is_secret:
            relevant = [a for a in self.articles if a.trigger_event_type]
        else:
            relevant = [a for a in self.articles if not a.trigger_event_type]
        if not relevant:
            return False
        return all(a.id in unlocked_article_ids for a in relevant)