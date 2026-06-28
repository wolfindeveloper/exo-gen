from dataclasses import dataclass, field

from app.domain.events.base import DomainEvent


@dataclass
class AggregateRoot:
    _events: list[DomainEvent] = field(default_factory=list, repr=False, init=False)

    def register_event(self, event: DomainEvent) -> None:
        self._events.append(event)
