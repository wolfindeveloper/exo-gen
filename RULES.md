# PROJECT CONTEXT
Это коммерческий backend-проект на FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL.
Архитектура: Domain-Driven Design (DDD) + Clean/Hexagonal Architecture.

# STRICT ARCHITECTURE RULES (НЕ НАРУШАТЬ!)
1. **Domain слой** (`src/app/domain/`) — ЧИСТЫЙ Python. Никаких импортов FastAPI, SQLAlchemy, Pydantic, Redis, httpx.
   - Entities — `@dataclass`, наследуются от `AggregateRoot`
   - Value Objects — `@dataclass(frozen=True)`
   - Repository Interfaces — `ABC` с `async` методами
   - Domain Events — `@dataclass(frozen=True)`, наследуются от `DomainEvent`
   - Domain Services — чистая бизнес-логика
   - Domain Exceptions — наследуются от `DomainError`

2. **Application слой** (`src/app/application/`) — Use Cases + DTOs.
   - Use Cases оркестрируют работу через репозитории и UoW
   - DTOs — Pydantic v2 модели (`BaseModel`, `ConfigDict(from_attributes=True)`)
   - НИКАКИХ прямых запросов к БД! Только через Repository Interfaces

3. **Infrastructure слой** (`src/app/infrastructure/`) — Технические детали.
   - SQLAlchemy ORM модели (`DeclarativeBase`)
   - Реализации репозиториев (наследуют ABC из domain)
   - Mappers — конвертация Domain ↔ ORM (в `mappers.py`)
   - UnitOfWork — управление транзакциями + dispatch Domain Events

4. **Presentation слой** (`src/app/presentation/`) — FastAPI routes.
   - Только DI через `Depends()`
   - Ловим `DomainError` и маппим в `HTTPException`
   - НЕ пишем бизнес-логику в роутах!

# CODING STANDARDS
- Python 3.12+, type hints везде
- Pydantic v2 (используй `model_config = ConfigDict(from_attributes=True)`)
- SQLAlchemy 2.0 async (`Mapped`, `mapped_column`, `select()`)
- UUID для всех PK
- Domain Events диспатчатся через `UnitOfWork.commit()` ПОСЛЕ коммита
- UnitOfWork.track() для аггрегатов, которые изменились