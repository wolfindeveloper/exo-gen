import hmac
import hashlib
import json
import time
from urllib.parse import parse_qs

from fastapi import Header, HTTPException, Depends

from app.presentation.api.dependencies import (
    get_player_repo,
    get_inventory_repo,
    get_loot_box_repo,
    get_uow,
)
from app.application.use_cases.auto_register_player import AutoRegisterPlayerUseCase
from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService
from app.config.settings import settings


def verify_telegram_signature(init_data: str) -> dict:
    """Проверяет подпись Telegram и возвращает данные о пользователе"""
    try:
        # Парсим строку вида "user=...&auth_date=...&hash=..."
        parsed_data = parse_qs(init_data)
        data_dict = {k: v[0] for k, v in parsed_data.items()}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid init data format")

    received_hash = data_dict.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash")

    # Проверка auth_date для защиты от replay-атак
    auth_date_str = data_dict.get("auth_date")
    if auth_date_str is None:
        raise HTTPException(status_code=401, detail="Missing auth_date")
    try:
        auth_date = int(auth_date_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid auth_date format")
    now = int(time.time())
    if now - auth_date > settings.TELEGRAM_AUTH_MAX_AGE_SECONDS:
        raise HTTPException(
            status_code=401,
            detail="Auth data too old. Possible replay attack.",
        )

    # 1. Сортируем ключи по алфавиту и склеиваем в строку
    sorted_items = sorted(data_dict.items())
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_items])

    # 2. Создаем секретный ключ (HMAC-SHA256 от "WebAppData" и токена бота)
    secret_key = hmac.new(
        b"WebAppData", settings.BOT_TOKEN.encode("utf-8"), hashlib.sha256
    ).digest()

    # 3. Считаем хэш от строки данных
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # 4. Сравниваем хэши
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=401, detail="Invalid Telegram signature. Hacker detected!"
        )

    # Достаем JSON с данными юзера
    user_json = data_dict.get("user", "{}")
    return json.loads(user_json)


async def get_current_player(
    authorization: str = Header(..., description="tghash <init_data>"),
    player_repo: PlayerRepository = Depends(get_player_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    uow: UnitOfWork = Depends(get_uow),
) -> Player:
    if not authorization.startswith("tghash "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")

    init_data = authorization.replace("tghash ", "")

    user_data = verify_telegram_signature(init_data)
    telegram_id = user_data.get("id")
    username = (
        user_data.get("username")
        or user_data.get("first_name")
        or f"user_{telegram_id}"
    )

    if not telegram_id:
        raise HTTPException(status_code=401, detail="User ID not found in init data")

    player = await player_repo.get_by_telegram_id(int(telegram_id))
    if not player:
        use_case = AutoRegisterPlayerUseCase(
            player_repo,
            loot_box_service=LootBoxService(),
            loot_box_repo=loot_box_repo,
            inventory_repo=inventory_repo,
        )
        player = await use_case.execute(int(telegram_id), username, uow)

    return player


async def get_admin_player(
    current_player: Player = Depends(get_current_player),
) -> Player:
    if current_player.telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")
    return current_player
