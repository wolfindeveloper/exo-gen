# 📖 EXO GENESIS: Полный контекст проекта

> Автогенерерированная документация для восстановления контекста в новой AI-сессии. Дата: Май 2026.

---

## 🏗 Архитектура и технологический стек

**EXO GENESIS** — TON-based Telegram Mini App (TMA) игра с config-driven архитектурой. Все игровые параметры (названия, цены, шансы, формулы) вынесены в JSON-конфиги. Код не содержит хардкода.

### Бэкенд
- **Python 3.12**, менеджер пакетов `uv`
- **FastAPI** — асинхронный REST API
- **Pydantic v2** — валидация конфигов при старте + схемы запросов/ответов
- **SQLAlchemy 2.0 async** — ORM с async/await
- **PostgreSQL 16** — основная БД (Docker)
- **Redis 7** — кэш конфигов, таймеры экспедиций, лидерборды (Docker)
- **Celery + Redis** — фоновые задачи (таймеры экспедиций, пуши)
- **TON SDK (tonutils)** — мок-клиент для блокчейна (testnet)

### Фронтенд
- **React 18** + **Vite** + **TypeScript**
- **Tailwind CSS** — тёмная космическая тема (#0B0F19, #1A1F2E), неоновые акценты (cyan-500, purple-500)
- **Framer Motion** — анимации (левитация, shimmer, пульсация, переходы)
- **Zustand** — управление состоянием (player, configs)
- **axios** — HTTP-клиент с авто-интерцептором X-Telegram-User
- **@twa-dev/sdk** — Telegram Web App SDK
- **@tonconnect/ui-react** — TON Connect для кошелька
- **lucide-react** — иконки

### UI-подход
- Компоненты v0.app интегрированы: glassmorphism, neon glow, анимации
- Все карточки динамические: принимают `slug` или `config_object`, рендерятся из JSON
- i18n: RU/EN/LA через `locales/*.json` и `config/*[name/description][lang]`

---

## 📂 Полная структура проекта

```
exo-gen/
├── spec.md                          # Полный технический паспорт проекта (источник истины)
├── .agent_skills.md                 # Инструкции для AI-агента (правила, запреты, workflow)
├── pyproject.toml                   # uv проект: зависимости, ruff, mypy, pytest
├── .env                             # Переменные окружения (dev)
├── .env.example                     # Шаблон .env для новых разработчиков
├── .gitignore                       # Исключения для git
├── docker-compose.yml               # PostgreSQL 16 + Redis 7 + API + Worker
├── Dockerfile.api                   # Docker-образ для API
├── Dockerfile.worker                # Docker-образ для Celery Worker
├── README.md                        # Краткое описание + quick start
│
├── core/                            # Ядро бэкенда
│   ├── __init__.py
│   ├── config.py                    # Pydantic Settings для .env (DATABASE_URL, REDIS_URL, JWT, TON и т.д.)
│   ├── config_loader.py             # Загрузка и кэширование config/*.json
│   ├── database.py                  # Async SQLAlchemy engine, session, init_db() (авто-создание таблиц)
│   ├── models.py                    # ORM модели: Player, Ship, Expedition, Artifact, PlayerInventory, XgenTransaction
│   └── redis.py                     # Async Redis клиент, set_json/get_json, тест подключения
│
├── api/                             # FastAPI приложение
│   ├── __init__.py
│   ├── main.py                      # Точка входа: lifespan, CORS, middleware логирования, роутеры
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py                  # get_current_player() — парсит X-Telegram-User header
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                  # POST /auth/telegram, POST /auth/worldid, GET /auth/me
│   │   ├── player.py                # GET /player/me — профиль игрока
│   │   ├── configs.py               # GET /config/{name} — отдаёт JSON из config/
│   │   ├── expeditions.py           # POST /expeditions/start, GET /expeditions/{id}, GET /expeditions/active
│   │   ├── laboratory.py            # POST /laboratory/craft, GET /laboratory/domains, GET /laboratory/recipes/{hash}
│   │   ├── artifacts.py             # GET /artifacts, POST /{id}/stake|unstake|claim-yield|calibrate
│   │   └── wallet.py                # POST /wallet/connect, GET /wallet/balance, GET /wallet/nft
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── player.py                # PlayerRead, PlayerUpdate
│   │   ├── expedition.py            # ExpeditionStartRequest, ExpeditionRead, ActiveExpeditionRead
│   │   ├── laboratory.py            # CraftRequest, CraftResponse, RecipeInfo
│   │   ├── artifact.py              # ArtifactRead, StakeResponse, ClaimYieldResponse, CalibrateResponse
│   │   └── wallet.py                # WalletConnectRequest/Response, WalletBalanceResponse
│   └── services/
│       ├── __init__.py
│       ├── expedition_service.py    # start_expedition(), get_expedition(), get_active_expeditions()
│       ├── overdrive_service.py     # calculate_overdrive_result(), roll_essence_drop()
│       ├── laboratory_service.py    # attempt_craft(), get_recipe_info()
│       ├── erosion_yield_service.py # update_artifact_cycles(), calculate_staking_yield(), calibrate_artifact()
│       └── nft_service.py           # mint_fleet_nft_if_eligible(), mint_artifact_nft(), mint_pilot_sbt()
│
├── blockchain/                      # Блокчейн-интеграция
│   ├── __init__.py
│   └── ton_client.py                # TonClient — мок-клиент для TON (баланс, минт NFT, транзакции)
│
├── contracts/                       # Tact смарт-контракты (стабы)
│   ├── __init__.py
│   ├── XGENJetton.tact              # TEP-74 Jetton (минт/берн/emergency halt)
│   ├── FleetNFT.tact                # TEP-62 Fleet NFT (T4-T5 корабли)
│   └── ArtifactNFT.tact             # TEP-62 Artifact NFT (1-of-1, уникальность по хэшу)
│
├── config/                          # Игровые конфиги (источник истины)
│   ├── fuels.json                   # 15 видов топлива T1-T5
│   ├── ships.json                   # 5 кораблей (Seeker → Apex)
│   ├── expeditions.json             # 5 экспедиций (Scrap Run → Genesis Point)
│   ├── overdrive.json               # Stable / Push / Overdrive режимы
│   ├── repair_costs.json            # Standard / Express / Hybrid / Auto / Catastrophic
│   ├── artifact_erosion.json        # Износ артефактов + staking yield (пул 40M)
│   ├── essence_drop.json            # Дроп эссенций + анти-фарм лимиты
│   ├── lab_rules.json               # Правила крафта (3-5 эссенций, SHA-256)
│   ├── galaxy_zones.json            # 5 секторов галактики
│   ├── marketplace.json             # Комиссии, роялти, внешний маркетплейс
│   ├── nft_minting.json             # Параметры NFT минтинга (TEP-62)
│   ├── notifications.json           # 4 шаблона уведомлений
│   ├── seasons.json                 # Сезон 1 (90 дней, веса, награды)
│   ├── shop_boxes.json              # Promotion crates (T2, T3)
│   ├── promotion_quests.json        # Квесты восхождения
│   ├── ranks.json                   # Ранги + формула XP (100 × Level^1.8)
│   └── avatars.json                 # Аватары игроков
│
├── locales/                         # Локализация
│   ├── ranks.json                   # RU/EN/LA названия рангов
│   └── common.json                  # Общие строки
│
├── workers/                         # Celery workers
│   ├── __init__.py
│   ├── celery_app.py                # Celery application factory
│   └── expedition_worker.py         # complete_expedition() — генерация лута, XP, essences
│
├── scripts/                         # Утилиты
│   └── seed_dev_data.py             # Сидер тестовых данных (player_123, корабль, топливо, эссенции)
│
├── tests/                           # Тесты
│   └── __init__.py
│
└── frontend/                        # React TMA фронтенд
    ├── package.json                 # Зависимости: react, vite, tailwind, framer-motion, zustand, axios
    ├── vite.config.ts               # Vite конфиг + прокси /api → backend
    ├── tsconfig.json                # TypeScript конфиг
    ├── tailwind.config.js           # Tailwind: cosmic-bg, neon-cyan/purple, rarity glow
    ├── postcss.config.js
    ├── index.html
    ├── .env                         # VITE_API_URL, VITE_TON_MANIFEST_URL
    ├── .env.example
    ├── public/
    │   └── tonconnect-manifest.json # Manifest для TON Connect
    └── src/
        ├── main.tsx                 # Точка входа: TON Connect Provider, TMA init, App
        ├── App.tsx                  # Router layout: TopBar + Routes + BottomNav + SettingsModal
        ├── router.tsx               # Типы маршрутов
        ├── index.css                # Tailwind + custom компоненты (card, btn, modal, scrollbar)
        ├── vite-env.d.ts            # Типы Vite env vars
        ├── lib/
        │   ├── api.ts               # Axios instance + авто X-Telegram-User header (mock для dev)
        │   └── api-helpers.ts       # Typed helpers: startExpedition(), craftArtifact(), stakeArtifact()
        ├── store/
        │   ├── usePlayerStore.ts    # Zustand: player state, mock fallback, updateBalance()
        │   └── useConfigStore.ts    # Zustand: ships, zones, expeditions, avatars из /config/*
        ├── types/
        │   └── index.ts             # Все TS интерфейсы: PlayerRead, ShipConfig, ExpeditionConfig, и т.д.
        ├── components/
        │   ├── HangarCard.tsx       # Карточка корабля v0: glassmorphism, rarity glow, Stats, LaunchButton
        │   ├── LaunchButton.tsx     # Кнопка "В экспедицию" с shimmer-анимацией
        │   ├── Spaceship.tsx        # SVG корабль с левитацией, цвет по тиру
        │   ├── Starfield.tsx        # Canvas анимированное звёздное поле
        │   ├── StatSlot.tsx         # Стеклянная карточка стата с иконкой
        │   ├── Toast.tsx            # Система уведомлений (success/error/info)
        │   ├── cards/
        │   │   ├── ShipCard.tsx     # Старая карточка корабля (заменена на HangarCard)
        │   │   └── ZoneCard.tsx     # Старая карточка зоны (заменена на inline в UniversePage)
        │   ├── layout/
        │   │   ├── TopBar.tsx       # Верхняя панель: аватар, имя, ранг, XP-бар, XGEN, настройки
        │   │   ├── BottomNav.tsx    # Нижнее меню: 🚀 Hangar | ⚡ Galaxy | 🧪 Laba
        │   │   ├── SubMenu.tsx      # Вкладки внутри страниц (SHIPS/RESOURCES, SECTORS/MAP/LORE)
        │   │   └── TabNavigation.tsx # Старая навигация (не используется)
        │   └── modals/
        │       ├── SettingsModal.tsx # Язык, ник, аватар, музыка, TON Connect
        │       ├── ShipModal.tsx     # Детали корабля + ремонт/запуск
        │       └── ZoneModal.tsx     # Детали зоны + лор + дроп-таблица
        └── pages/
            ├── HangarPage.tsx       # 🚀 Hangar: SubMenu(SHIPS/RESOURCES) + HangarCards + Starfield
            ├── UniversePage.tsx     # ⚡ Galaxy: SubMenu(SECTORS/MAP/LORE) + ZoneCards + интерактивная карта
            └── LaboratoryPage.tsx   # 🧪 Laba: SubMenu(CRAFT/ESSENCES/STAKING) + крафт + стейкинг
```

---

## ⚙️ Запуск и окружение

### Бэкенд (локальная разработка)

```powershell
# 1. Активировать venv (если не активирован)
.\.venv\Scripts\activate

# 2. Запустить PostgreSQL + Redis в Docker
docker compose up -d postgres redis

# 3. Засидить тестовые данные (player_123, корабль, топливо, эссенции)
uv run python scripts/seed_dev_data.py

# 4. Запустить FastAPI сервер
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Фронтенд

```powershell
cd frontend
npm run dev
# Откроется на http://localhost:5173
```

### Проверка работы

```powershell
# Бэкенд health check
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing

# Swagger UI
# Открыть в браузере: http://127.0.0.1:8000/docs

# Конфиги
Invoke-WebRequest -Uri "http://127.0.0.1:8000/config/ships" -UseBasicParsing

# Фронтенд
# Открыть в браузере: http://localhost:5173
```

### Docker (полный стек)

```bash
docker compose down -v && docker compose up -d
# Поднимает: postgres:5434, redis:6379, api:8000, worker
```

---

## 🔑 Конфигурация и важные нюансы

### .env (ключевые переменные)

| Переменная | Значение (dev) | Описание |
|---|---|---|
| `POSTGRES_USER` | `dev` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | `devpassword` | Пароль PostgreSQL |
| `POSTGRES_DB` | `exogenesis` | Имя базы данных |
| `DATABASE_URL` | `postgresql+asyncpg://dev:devpassword@localhost:5434/exogenesis` | Async SQLAlchemy URL |
| `DATABASE_URL_SYNC` | `postgresql://dev:devpassword@localhost:5434/exogenesis` | Sync URL для Alembic |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis для кэша |
| `TELEGRAM_BOT_TOKEN` | `test_bot_token_for_dev` | Токен бота (mock) |
| `JWT_SECRET` | `dev_jwt_super_secret_key...` | Секрет для JWT |
| `TON_NETWORK` | `testnet` | Сеть TON |

### Mock-авторизация для dev

В `frontend/src/lib/api.ts` автоматически добавляется header `X-Telegram-User` с моковыми данными:
```json
{"id": 123, "username": "Navigator", "first_name": "Test"}
```
Это позволяет тестировать без Telegram Web App.

### CORS

В `api/main.py` разрешены все origins (`allow_origins=["*"]`) — только для dev. Для продакшена нужно ограничить.

### Авто-создание таблиц

При старте FastAPI в `lifespan` вызывается `init_db()` → `Base.metadata.create_all`. Это создаёт все таблицы, если их нет. **Безопасно**: не удаляет существующие данные. Alembic отключён для dev-скорости.

### v0 компоненты

Интегрированы из `./v0-export/` (папка удалена после интеграции):
- **Starfield.tsx** — Canvas звёздное поле, фон всех страниц
- **Spaceship.tsx** — SVG корабль с левитацией, цвет зависит от `tier` пропса
- **LaunchButton.tsx** — Кнопка "В экспедицию" с shimmer-анимацией, пульсирующим glow
- **HangarCard.tsx** — Полная карточка корабля: glassmorphism, rarity glow, StatSlot grid, LaunchButton

### Структура config JSON

Все конфиги предметов следуют паттерну:
```json
{
  "item_slug": {
    "name": { "ru": "...", "en": "...", "la": "..." },
    "description": { "ru": "...", "en": "...", "la": "..." },
    "image_path": "/assets/...",
    "tier": 1,
    "slug": "item_slug"
  }
}
```

**Важно:** `config/galaxy_zones.json` имеет обёртку `{ "galaxy_zones": { ... } }`. `useConfigStore` автоматически разворачивает её.

---

## 🤖 Инструкции для AI-агента в новой сессии

### Как читать этот файл

1. **spec.md** — единственный источник истины. Если конфликт с "лучшими практиками" → следуем spec.md.
2. **CONFIG-DRIVEN** — никогда не хардкодь названия, цены, шансы, пути. Всё из `config/*.json`.
3. **SLUG SYSTEM** — в БД и API хранится только `slug`. Локализация на фронтенде.

### Что НЕЛЬЗЯ менять без явного запроса

- **Dockerfile.api / Dockerfile.worker** — уже настроены для продакшена
- **docker-compose.yml** — credentials синхронизированы с .env
- **Структуру config/*.json** — поля `name`, `description`, `image_path`, `tier`, `slug` обязательны
- **Alembic** — отключён для dev, но нужен для продакшена

### Как восстанавливать состояние БД

```powershell
# Удалить и пересоздать таблицы
docker compose down -v && docker compose up -d postgres redis
uv run python scripts/seed_dev_data.py
```

Сидер создаёт:
- Player `player_123` (telegram_id=123, 1000 $XGEN)
- Корабль `seeker_dust_runner` (T1, stability=100)
- 50× `fuel_t1_mangan_hydride`
- 10× `essence_t1`, `essence_t2`, `essence_t3`

Сидер **идемпотентен** — пропускает существующие записи.

### Команды запуска (шпаргалка)

```powershell
# Бэкенд
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Фронтенд
cd frontend && npm run dev

# БД + Redis
docker compose up -d postgres redis

# Сидер
uv run python scripts/seed_dev_data.py

# Сборка фронтенда
cd frontend && npm run build

# Линтинг
uv run ruff check .
uv run mypy .
```

### Куда двигаться дальше

Следующий этап — **Phase 5: Тестирование и Alpha** (раздел 22 spec.md):
1. Unit-тесты для сервисов (expedition, overdrive, laboratory)
2. Integration-тесты для API роутеров
3. Load-тест (1k concurrent users)
4. Валидация баланса Burn/Emission
5. Alpha-тест на 500 игроков

---

## 🗺 Текущий статус и следующий шаг

### ✅ Выполненные фазы

| Фаза | Описание | Статус |
|---|---|---|
| **Phase 0** | Инициализация проекта, uv, docker-compose, config/*.json | ✅ |
| **Phase 1** | Backend Foundation: config, database, redis, auth, player, configs routers | ✅ |
| **Phase 2** | Game Mechanics: expedition, overdrive, laboratory, erosion_yield сервисы + Celery worker | ✅ |
| **Phase 3** | Blockchain Integration: TON client (mock), NFT service, wallet router, Tact contracts | ✅ |
| **Phase 4** | Frontend TMA: React + Vite + Tailwind + Framer Motion + v0 components | ✅ |
| **Phase 4.5** | Full feature integration: Hangar/Galaxy/Laba pages, API helpers, Toast, SubMenu | ✅ |
| **Bug Fixes** | TopBar mock fallback, ZoneCard null checks, DB credentials sync, auto table creation | ✅ |
| **Dev Seeder** | scripts/seed_dev_data.py — идемпотентный сидер тестовых данных | ✅ |

### 🎮 Готовые механики

- **Экспедиции:** Запуск, валидация корабля/топлива/тира, рандомизация длительности, Celery-завершение
- **Overdrive:** Stable/Push/Overdrive режимы, множители лута, расчёт урона со стабильностью
- **Лаборатория:** SHA-256 хэш, проверка уникальности, 100% burn $XGEN, 50% возврат эссенций
- **Эрозия:** Циклы артефактов, dormant статус, calibration
- **Стейкинг:** Расчёт дохода, activity multiplier, global pool 40M, claim yield
- **NFT:** Минтинг T4-T5 кораблей, 1-of-1 артефактов, Pilot SBT (мок)
- **Кошелёк:** Connect/balance/disconnect (TON Connect UI)

### 📋 Открытые задачи (Phase 5)

- [ ] Unit-тесты для `api/services/*.py`
- [ ] Integration-тесты для `api/routers/*.py`
- [ ] Pydantic-валидация конфигов при старте (lifespan)
- [ ] Redis кэширование конфигов с TTL
- [ ] Rate limiting middleware
- [ ] Celery beat для ежедневных начислений (Daily Check-in)
- [ ] Push-уведомления через Telegram Bot API
- [ ] Alembic миграции для продакшена
- [ ] Grafana/Loki мониторинг
- [ ] CI/CD через GitHub Actions
