from typing import Callable
from collections import defaultdict

from app.domain.events.base import DomainEvent


class DomainEventDispatcher:
    def __init__(self):
        self._handlers: dict[type[DomainEvent], list[Callable]] = defaultdict(list)

    def register(self, event_type: type[DomainEvent], handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            await handler(event)


dispatcher = DomainEventDispatcher()
