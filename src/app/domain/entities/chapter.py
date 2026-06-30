from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    reward_items: list[dict] = field(default_factory=list)
    articles: list["Article"] = field(default_factory=list)
    deleted_at: datetime | None = None

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        is_secret: bool | None = None,
        reward_xgen: int | None = None,
        reward_fragments: int | None = None,
        reward_items: list[dict] | None = None,
        **kwargs: object,
    ) -> None:
        if "season_id" in kwargs:
            raise ValueError("Cannot change season_id directly")
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if is_secret is not None:
            self.is_secret = is_secret
        if reward_xgen is not None:
            self.reward_xgen = reward_xgen
        if reward_fragments is not None:
            self.reward_fragments = reward_fragments
        if reward_items is not None:
            self.reward_items = reward_items

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None

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