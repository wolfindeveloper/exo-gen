from dataclasses import dataclass
from uuid import UUID

@dataclass
class Article:
    id: UUID
    chapter_id: UUID
    title: str
    content: str
    
    # Условия открытия (выбирается что-то одно):
    fragment_cost: int = 0                 # Купить за фрагменты
    trigger_event_type: str | None = None  # Открыть триггером
    required_item_id: UUID | None = None   # Открыть с помощью предмета (НОВОЕ!)
    
    trigger_threshold: int = 1 