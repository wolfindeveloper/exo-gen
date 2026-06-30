from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

@dataclass
class Article:
    id: UUID
    chapter_id: UUID
    title: str
    content: str
    fragment_cost: int = 0
    trigger_event_type: str | None = None
    required_item_id: UUID | None = None
    trigger_threshold: int = 1
    deleted_at: datetime | None = None

    def update(
        self,
        title: str | None = None,
        content: str | None = None,
        fragment_cost: int | None = None,
        trigger_event_type: str | None = None,
        trigger_threshold: int | None = None,
        required_item_id: UUID | None = None,
        **kwargs: object,
    ) -> None:
        if "chapter_id" in kwargs:
            raise ValueError("Cannot change chapter_id directly")
        if title is not None:
            self.title = title
        if content is not None:
            self.content = content
        if fragment_cost is not None:
            self.fragment_cost = fragment_cost
        if trigger_event_type is not None:
            self.trigger_event_type = trigger_event_type
        if trigger_threshold is not None:
            self.trigger_threshold = trigger_threshold
        if required_item_id is not None:
            self.required_item_id = required_item_id

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None 