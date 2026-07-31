# IMPLEMENTATION_REPORT.md

> Дата проверки: 2026-07-31
> Фаза: Pre-production review

---

## Механика 6: Путеводитель (Guide)

### GetGuideUseCase
**Файл:** `src/app/application/use_cases/get_guide.py`

| Проверка | Статус | Описание |
|----------|--------|----------|
| Seasonal chapters filtering | ✅ OK | Строки 28-39: проверяется `season.is_currently_active()`, кэширует результат |
| Cache для сезонов | ✅ OK | `season_cache: dict[UUID, bool]` предотвращает повторные запросы |
| Скрытые главы | ✅ OK | Секретные главы отображаются, сезонные скрываются при истечении |
| Content hiding | ✅ OK | Контент статьи скрыт если не открыта (строка 48) |

**Проблем:** Не найдено

---

### UnlockArticleUseCase
**Файл:** `src/app/application/use_cases/unlock_article.py`

| Проверка | Статус | Описание |
|----------|--------|----------|
| Fragments deduction | ✅ OK | Строка 84: `player.spend_fragments(article.fragment_cost)` |
| Key item validation | ✅ OK | Строки 78-82: проверка `required_item_id` |
| Season validation | ✅ OK | Строки 69-74: проверка `is_currently_active()` |
| Chapter completion check | ✅ OK | Строки 108-137: проверка завершения главы |
| Double unlock prevention | ✅ OK | Строка 64-67: проверка `is_article_unlocked` |

**Проблем:** Не найдено

---

### ProcessTriggerUseCase
**Файл:** `src/app/application/use_cases/process_trigger.py`

| Проверка | Статус | Описание |
|----------|--------|----------|
| Trigger types support | ✅ OK | Фильтрация по `art.trigger_event_type == dto.event_type` (строка 68) |
| Threshold tracking | ✅ OK | `progress.increment(article.trigger_threshold)` (строка 92) |
| Auto-unlock on threshold | ✅ OK | Автоматическое открытие при достижении порога |
| Chapter completion | ✅ OK | Проверка завершения главы после открытия статьи |
| Season validation | ✅ OK | Строки 95-102: проверка сезона перед открытием |

**Проблем:** Не найдено

---

## Механика 7: Магазин (Shop)

### PurchaseShopItemUseCase
**Файл:** `src/app/application/use_cases/purchase_shop_item.py`

| Проверка | Статус | Описание |
|----------|--------|----------|
| Race condition (FOR UPDATE) | ✅ OK | Строка 44: `player_repo.get_by_id_for_update()` |
| Daily limit check | ✅ OK | Строка 55-57: `get_purchase_count_today()` |
| Stock limit check | ✅ OK | Строка 58-60: `get_total_purchase_count()` + `shop_item.can_purchase()` |
| Bundle items | ✅ OK | Строки 67-75: итерация по `shop_item.bundle_items` |
| XGen spend | ✅ OK | Строка 64: `locked_player.spend_xgen(shop_item.price_xgen)` |

**Проблем:**

#### ПРОБЛЕМА #1: Нет валидации stock_limit перед покупкой
**Критичность:** LOW
**Описание:** `stock_limit` проверяется в `can_purchase()`, но:
- `stock_limit = 0` означает "без ограничений" (строка 55 в `shop.py`: `if self.stock_limit > 0`)
- Это корректная логика, но нет защиты от создания предметов с `stock_limit < total_purchases`

**Рекомендация:** Добавить валидацию при создании/обновлении `ShopItem`:
```python
def update(self, stock_limit: int | None = None):
    if stock_limit is not None and stock_limit > 0:
        if stock_limit < self.total_purchases:
            raise ValueError("stock_limit cannot be less than total purchases")
```

---

## Механика 8: Лидерборд (Leaderboard)

### GetMultiMetricLeaderboardUseCase
**Файл:** `src/app/application/use_cases/get_multi_metric_leaderboard.py`

| Проверка | Статус | Описание |
|----------|--------|----------|
| Rank return for current player | ✅ OK | Строки 25, 28, 31, 34, 37: `get_player_rank_by_*()` |
| 5 metrics supported | ✅ OK | XP, expeditions, artifacts, xgen, articles |
| Top 100 returned | ✅ OK | `limit=100` во всех запросах |

**Проблемы:**

#### ПРОБЛЕМА #2: Отсутствуют индексы для leaderboard запросов
**Критичность:** MEDIUM
**Описание:** Запросы сортируют по `xp`, `total_expeditions`, `total_artifacts_found`, `xgen_balance`, но в `PlayerORM` нет индексов для этих колонок.

**Текущие индексы в PlayerORM:**
- `id` (PK)
- `telegram_id` (unique)

**Нужные индексы:**
```sql
CREATE INDEX idx_players_xp ON players(xp DESC);
CREATE INDEX idx_players_total_expeditions ON players(total_expeditions DESC);
CREATE INDEX idx_players_total_artifacts_found ON players(total_artifacts_found DESC);
CREATE INDEX idx_players_xgen_balance ON players(xgen_balance DESC);
```

**Рекомендация:** Создать Alembic миграцию с индексами.

#### ПРОБЛЕМА #3: N+1 query problem в rank calculation
**Критичность:** LOW
**Описание:** `get_player_rank_by_*()` делает 2 запроса:
1. Получить значение игрока
2. COUNT игроков с бо́льшим значением

При 100+ игроках это 200 запросов. Можно оптимизировать через window functions.

---

## Механика 9: Профиль (Profile)

### GetProfileUseCase
**Файл:** `src/app/application/use_cases/get_profile.py`

| Проверка | Статус | Описание |
|----------|--------|----------|
| XP/level | ✅ OK | Строка 29-30 |
| Total expeditions | ✅ OK | Строка 31 |
| Total artifacts | ✅ OK | Строка 32 |
| Unlocked articles | ✅ OK | Строка 33 |
| Articles total | ✅ OK | Строка 39 (через chapter_repo) |

**Проблемы:**

#### ПРОБЛЕМА #4: Отсутствует кэширование профиля в Redis
**Критичность:** LOW
**Описание:** Каждый запрос профиля делает SELECT из БД. При частых обновлениях (после каждой экспедиции) это может быть bottleneck.

**Рекомендация:** Добавить кэширование на 60 секунд:
```python
async def execute(self, player: Player) -> ProfileResponseDTO:
    cache_key = f"profile:{player.id}"
    cached = await self.redis.get(cache_key)
    if cached:
        return ProfileResponseDTO(**cached)
    
    # ... existing logic ...
    
    await self.redis.set(cache_key, response.model_dump(), ex=60)
    return response
```

**Статус:** Не реализовано (требуется доработка)

#### ПРОБЛЕМА #5: Дублирование данных в DTO
**Критичность:** LOW
**Описание:** `total_expeditions` = `expeditions_completed`, `total_artifacts_found` = `artifacts_found`, `unlocked_articles` = `articles_read`

**Рекомендация:** Упростить DTO или вычисляемые поля.

---

## Механика 10: Настройки (Settings)

### UpdatePlayerSettingsUseCase
**Файл:** `src/app/application/use_cases/update_player_settings.py`

| Проверка | Статус | Описание |
|----------|--------|----------|
| Language validation | ⚠️ PARTIAL | Принимает любую строку, нет валидации допустимых языков |
| Music enabled | ✅ OK | Boolean без ограничений |
| Default settings | ✅ OK | Строка 20: создается `PlayerSettings(player_id=player_id)` с defaults |

**Проблемы:**

#### ПРОБЛЕМА #6: Нет валидации допустимых языков
**Критичность:** MEDIUM
**Описание:** `dto.language` может быть любой строкой ("xyz", "123", ""). Фронтенд поддерживает `["ru", "en", "ua"]`.

**Рекомендация:** Добавить валидацию:
```python
VALID_LANGUAGES = {"ru", "en", "ua"}

if dto.language is not None:
    if dto.language not in VALID_LANGUAGES:
        raise ValueError(f"Invalid language: {dto.language}")
    settings.language = dto.language
```

#### ПРОБЛЕМА #7: Нет music_enabled валидации
**Критичность:** LOW
**Описание:** Принимает любой bool, нет ограничений.

---

## Сводная таблица найденных проблем

| # | Механика | Проблема | Критичность | Статус |
|---|----------|----------|-------------|--------|
| 1 | Shop | Нет валидации stock_limit при создании | LOW | Требует доработки |
| 2 | Leaderboard | Отсутствуют индексы для метрик | MEDIUM | **Требует миграции** |
| 3 | Leaderboard | N+1 в rank calculation | LOW | Оптимизация |
| 4 | Profile | Нет кэширования в Redis | LOW | Требует доработки |
| 5 | Profile | Дублирование данных в DTO | LOW | Рефакторинг |
| 6 | Settings | Нет валидации языков | MEDIUM | **Требует доработки** |
| 7 | Settings | music_enabled без ограничений | LOW | Опционально |

---

## Созданные тесты

**Файл:** `tests/test_use_cases/test_guide_mechanics.py`

| Тест | Описание |
|------|----------|
| `test_seasonal_chapter_hidden_when_expired` | Скрытая сезонная глава |
| `test_seasonal_chapter_shown_when_active` | Активная сезонная глава |
| `test_expired_seasonal_chapter_shown_if_completed` | Завершенная сезонная глава |
| `test_article_content_hidden_when_not_unlocked` | Скрытие контента |
| `test_fragments_deducted_on_unlock` | Списание фрагментов |
| `test_insufficient_fragments_raises_error` | Ошибка при нехватке фрагментов |
| `test_expedition_count_trigger` | Триггер экспедиции |
| `test_trigger_unlocks_after_threshold` | Открытие при достижении порога |

---

## Рекомендуемые действия

### Приоритет HIGH (перед релизом)
1. **Создать индексы для leaderboard** — Alembic миграция с индексами для `xp`, `total_expeditions`, `total_artifacts_found`, `xgen_balance`

### Приоритет MEDIUM (после релиза v1)
2. Добавить валидацию языков в `UpdatePlayerSettingsUseCase`
3. Добавить валидацию `stock_limit` при создании `ShopItem`
4. Добавить кэширование профиля в Redis

### Приоритет LOW (future)
5. Рефакторинг `ProfileResponseDTO` (убрать дублирование)
6. Оптимизация rank calculation через window functions
