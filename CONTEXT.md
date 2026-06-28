# CONTEXT.md — Hitchhiker Idle

> Полная документация проекта. Создан для быстрого погружения агентов и разработчиков.
> Обновляется после каждого этапа разработки.

---

## 📋 О проекте

**Hitchhiker Idle** — idle/clicker Telegram Mini App игра в тематике "Автостопом по галактике" (Douglas Adams).

**Суть**: Игрок управляет космическим кораблем, отправляет его в таймированные экспедиции в различные зоны, добывает ресурсы (XGen, Фрагменты), собирает предметы, управляет топливом ("чай") и прочностью ("оптимизм"), открывает статьи/главы Путеводителя, соревнуется в сезонных лидербордах.

**Слоган**: *"Don't Panic. Just idle through the galaxy."*

**Ссылки**:
- Telegram Bot: `@exo_genesis_bot`
- Frontend: `https://app.exo-gen.com`
- API: `https://api.exo-gen.com`
- Deploy: Coolify + Docker + Traefik (Let's Encrypt SSL)

---

## 🏗 Архитектура

### Бекенд (Python 3.12+)

**Стек**: FastAPI + SQLAlchemy 2.0 (async) + asyncpg + Alembic + Redis + Celery + Pydantic v2

**Паттерн**: Domain-Driven Design (DDD) с Clean/Hexagonal Architecture:

```
Presentation (FastAPI routes)
  → Application (Use Cases, DTOs)
    → Domain (Entities, Value Objects, Repository Interfaces, Domain Events)
      → Infrastructure (SQLAlchemy Repos, ORM Models, Mappers, UoW)
```

**Ключевые решения**:
- Domain entities — чистые Python dataclasses, без ORM-зависимостей
- Repository interfaces (ABC) в domain слое
- Infrastructure реализует интерфейсы через SQLAlchemy
- Mappers конвертируют domain entity ↔ ORM model
- Use Cases оркестрируют работу через repositories + Unit of Work
- Domain Events + dispatch через UnitOfWork

**Структура** (`src/app/`):

| Директория | Назначение |
|------------|-----------|
| `domain/entities/` | 12 entity: Player, Ship, Zone, Expedition, Item, Inventory, InventoryItem, Chapter, Article, Season, LeaderboardEntry, UnlockedArticle, ChapterCompletion, ArticleTriggerProgress |
| `domain/value_objects/` | TeaLevel, Optimism, XgenBalance, FragmentsBalance |
| `domain/events/` | 6 domain events (PlayerRegistered, DailyLoginCompleted, ExpeditionStarted, ExpeditionCompleted, ArticleUnlocked, ChapterCompleted) |
| `domain/exceptions/` | 8 категорий исключений (Player, Ship, Expedition, Zone, Guide, Inventory) |
| `domain/services/` | Clock (абстрактные часы), LootGenerator (рандом лут) |
| `domain/repositories/` | 7 abstract repository interfaces |
| `application/use_cases/` | 17 use cases (CreatePlayer, StartExpedition, ClaimExpedition, UnlockArticle, ProcessTrigger, UseItem и др.) |
| `application/dtos/` | Pydantic DTOs |
| `infrastructure/persistence/models/` | 10 SQLAlchemy ORM моделей |
| `infrastructure/persistence/repositories/` | 7 SQLAlchemy реализаций репозиториев |
| `infrastructure/persistence/mappers.py` | Мапперы domain → ORM |
| `presentation/api/routes/` | FastAPI роуты: admin, expeditions, guide, inventory, player, zones |

### Фронтенд (React 19 + TypeScript 6)

**Стек**: Vite 8 + Tailwind CSS v4 + Zustand 5 + react-router-dom 7 + motion 12 + lucide-react + i18n (в процессе)

**Структура** (`frontend/src/`):

| Директория | Назначение |
|------------|-----------|
| `pages/` | ShipPage (реализована), AdminPage (CRUD), Galaxy, GuidePage, Inventory, Profile, Shop |
| `components/` | NavBar, HudBar, ZoneCard, ZoneModal, HexSlot, SlotSelectModal, PageTransition, RewardSheet, SettingsSheet, BoxReveal |
| `store/` | game.ts (Zustand — состояние игры), settings.ts (настройки) |
| `api/` | client.ts (HTTP-клиент для всех endpoint'ов) |
| `hooks/` | useTimer, useCountUp, useTranslate, useNotifications |
| `lib/` | telegram, audio, animations, xp, ranks, stats, expeditionCalc, i18n |
| `types/` | Все TypeScript типы (28 интерфейсов) |

---

## 🎯 Текущее состояние (до этапа 0)

### ✅ Реализовано на бекенде
- DDD архитектура (сущности, value objects, use cases, репозитории)
- 12 таблиц в PostgreSQL, 8 миграций Alembic
- Аутентификация через Telegram HMAC-SHA256
- 20+ API endpoint'ов (игроки, зоны, экспедиции, путеводитель, инвентарь, админка)
- Ключевая бизнес-логика (экспедиции, ежедневные логины, loot система, открытие статей, лидерборды)



### ✅ Реализовано на фронтенде (Stage 3b)
- **6 страниц**: ShipPage (канвас/animated starfield, hex slots, экспедиции, easter eggs), Galaxy (карта зон по тирам), GuidePage (главы/статьи/глитчи), Inventory (фильтры/сортировка/использование предметов), Profile (статистика/достижения/прогресс), Shop (категории/покупки за XGEN/Stars), AdminPage (CRUD контента, дашборд)
- **9 компонентов**: HudBar (профиль/ресурсы/xp bar), ZoneCard, ZoneModal (расчет риска/бонусы артефактов), HexSlot, SlotSelectModal, RewardSheet (анимация лута), PageTransition, BoxReveal (стартовый бокс), SettingsSheet (язык/музыка)
- **4 хука**: useTimer (таймер экспедиций), useCountUp (анимация чисел), useTranslate (i18n), useNotifications (бейджи NavBar)
- **7 lib**: xp, ranks, stats, animations (framer variants), audio (музыка Free Music Archive), expeditionCalc (расчет риска/топлива), i18n (ru/en/ua)
- **API client**: 30+ endpoints (content, ships, guide, shop, achievements, stats, events)
- **Store**: game.ts (полное состояние + 20+ actions), settings.ts (localStorage persistence)
- **28 типов** в types/index.ts
- i18n: русский, украинский, английский
- BrowserLanding, Telegram WebApp интеграция
- AdminGate (защита `telegram_id === 754269918`)

---

## 📊 Оценка готовности к релизу

**Текущее состояние: ~65%**

Бекенд архитектурно хорош (DDD), все необходимые endpoint'ы реализованы.
Фронтенд — 6 из 6 страниц портированы, все компоненты/хуки/утилиты перенесены.

---

## 🗺 План этапов

| Этап | Что делаем | Статус |
|------|-----------|--------|
| **0** | Фундамент: CI/CD, Docker, pre-commit, тесты, секьюрити | ✅ Выполнен |
| **1** | Бекенд: Content, Ships, Stats, Guide Detail, Achievements, Shop, Events, Stars | ⏳ Stage 4 |
| **2** | Админка для заказчика (CRUD контента, дашборд) | ✅ Выполнен |
| **3** | Фронтенд: портирование старого фронта (6 страниц, компоненты, хуки, i18n) | ⏳ Stage 3a: admin panel frontend ✅ / Stage 3b: player pages ✅ |
| **4** | Бекенд Stage 1: Content API (`/content/ships|zones|resources|artifacts|ranks`), Ships API (profile patch, ships list, refuel/repair/equip/unequip), Stats API, Guide Detail, Achievements API, Shop API, Events API, Stars balance | ⏳ В плане |
| **5** | Монетизация: Telegram Stars, абстрактный платежный слой, реклама | ⏳ В плане |
| **6** | Контент + Полировка: наполнение, анимации, тесты, README | ⏳ В плане |

---

## 🔧 Технические заметки

- **Python**: 3.12+ (pyproject.toml, Dockerfile)
- **Пакетный менеджер**: `uv` (Astral)
- **Билд-система Python**: Hatch
- **База**: PostgreSQL (асинхронно через asyncpg)
- **Миграции**: Alembic (async)
- **Кэш**: Redis (настроен, не используется)
- **Очереди**: Celery + Redis (настроен, без задач)
- **Telegram**: Mini App + Bot API для отправки сообщений
- **Deploy**: Coolify + Traefik (docker-compose)
- **CI/CD**: GitHub Actions (lint → typecheck → test → build → Coolify webhook)
- **Pre-commit**: ruff, mypy, trailing-whitespace, end-of-file-fixer, check-yaml, detect-private-key
- **Тесты**: pytest (backend), vitest (frontend)

### Старый репозиторий
Ссылка: https://github.com/wolfindeveloper/exo-genesis
- Фронтенд с полным UI (все страницы, компоненты, хуки, утилиты)
- Бекенд на Supabase (упрощенная архитектура, без DDD) — НЕ ИСПОЛЬЗУЕМ, берем только UI
