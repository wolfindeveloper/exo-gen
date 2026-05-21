"""CLI-утилита для валидации всех игровых конфигов через Pydantic.

Использование:
    uv run python -m scripts.validate_configs

Выход с кодом 1, если хотя бы один конфиг невалиден (для CI/CD gate).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Фикс кодировки для Windows-консоли
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pydantic import ValidationError

# Добавляем корень проекта в sys.path для импортов из core/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.config_models import (
    ArtifactErosionConfig,
    AvatarsConfig,
    EssenceDropConfig,
    ExpeditionConfig,
    FuelConfig,
    GalaxyZoneEntry,
    LabRulesConfig,
    MarketplaceConfig,
    NftMintingConfig,
    NotificationsConfig,
    OverdriveConfig,
    PromotionQuestsConfig,
    RanksConfig,
    RepairCostEntry,
    SeasonsConfig,
    ShipConfig,
    ShopBoxesConfig,
)

CONFIG_DIR = PROJECT_ROOT / "config"

# Конфиги, которые валидируются как единый объект (не dict[str, item])
SINGLE_OBJECT_CONFIGS = {
    "overdrive.json": OverdriveConfig,
    "artifact_erosion.json": ArtifactErosionConfig,
    "essence_drop.json": EssenceDropConfig,
    "lab_rules.json": LabRulesConfig,
    "marketplace.json": MarketplaceConfig,
    "nft_minting.json": NftMintingConfig,
    "notifications.json": NotificationsConfig,
    "seasons.json": SeasonsConfig,
    "shop_boxes.json": ShopBoxesConfig,
    "promotion_quests.json": PromotionQuestsConfig,
    "ranks.json": RanksConfig,
    "avatars.json": AvatarsConfig,
}

# Конфиги, где каждый элемент валидируется отдельно (dict[str, item])
ITEM_CONFIGS: dict[str, type] = {
    "ships.json": ShipConfig,
    "fuels.json": FuelConfig,
    "expeditions.json": ExpeditionConfig,
    "repair_costs.json": RepairCostEntry,
    "galaxy_zones.json": GalaxyZoneEntry,
}


def validate_config_file(filename: str) -> tuple[bool, list[str]]:
    """Валидирует один JSON-файл через Pydantic-модель.

    Args:
        filename: Имя файла в директории config/.

    Returns:
        Кортеж (успех, список ошибок).
    """
    filepath = CONFIG_DIR / filename
    if not filepath.is_file():
        return False, [f"Файл не найден: {filepath}"]

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except json.JSONDecodeError as exc:
        return False, [f"Невалидный JSON: {exc}"]

    errors: list[str] = []

    # Однообъектные конфиги: валидируем целиком
    if filename in SINGLE_OBJECT_CONFIGS:
        model = SINGLE_OBJECT_CONFIGS[filename]
        try:
            model.model_validate(raw)
        except ValidationError as exc:
            errors = [f"  - {e['loc']}: {e['msg']}" for e in exc.errors()]
        return len(errors) == 0, errors

    # Конфиги-словари: валидируем каждый элемент отдельно
    if filename in ITEM_CONFIGS:
        model = ITEM_CONFIGS[filename]

        # galaxy_zones.json имеет обёртку {"galaxy_zones": {...}}
        if filename == "galaxy_zones.json":
            data = raw.get("galaxy_zones", raw)
        else:
            data = raw

        for slug, item_data in data.items():
            try:
                model.model_validate(item_data)
            except ValidationError as exc:
                for err in exc.errors():
                    loc = " → ".join(str(x) for x in err["loc"])
                    errors.append(f"  [{slug}] {loc}: {err['msg']}")

        return len(errors) == 0, errors

    return False, [f"Неизвестный конфиг: {filename}"]


def main() -> None:
    """Точка входа CLI: валидирует все конфиги и выводит отчёт."""
    print("🔍 Валидация игровых конфигов...\n")

    all_configs = {**SINGLE_OBJECT_CONFIGS, **ITEM_CONFIGS}
    total = len(all_configs)
    passed = 0
    failed = 0

    for filename in all_configs:
        ok, errors = validate_config_file(filename)
        if ok:
            passed += 1
            print(f"  ✅ {filename}")
        else:
            failed += 1
            print(f"  ❌ {filename}")
            for err in errors:
                print(f"    {err}")

    print()
    if failed == 0:
        print(f"✅ {passed}/{total} конфигов валидны")
        sys.exit(0)
    else:
        print(f"❌ {failed}/{total} конфигов содержат ошибки")
        sys.exit(1)


if __name__ == "__main__":
    main()
