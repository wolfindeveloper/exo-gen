import hmac
import hashlib
import json
import os
from urllib.parse import parse_qs
from fastapi import Header, HTTPException, Depends
from uuid import UUID
from dotenv import load_dotenv

from app.presentation.api.dependencies import get_player_repo 

from app.domain.entities.player import Player
from app.domain.repositories.player_repository import PlayerRepository


load_dotenv() 
# Убедись, что BOT_TOKEN добавлен в твой .env файл!
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in .env file")

def verify_telegram_signature(init_data: str) -> dict:
    """Проверяет подпись Telegram и возвращает данные о пользователе"""
    try:
        # Парсим строку вида "user=...&auth_date=...&hash=..."
        parsed_data = parse_qs(init_data)
        data_dict = {k: v[0] for k, v in parsed_data.items()}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid init data format")

    received_hash = data_dict.pop('hash', None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash")

    # 1. Сортируем ключи по алфавиту и склеиваем в строку
    sorted_items = sorted(data_dict.items())
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted_items])

    # 2. Создаем секретный ключ (HMAC-SHA256 от "WebAppData" и токена бота)
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode('utf-8'), hashlib.sha256).digest()
    
    # 3. Считаем хэш от строки данных
    calculated_hash = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # 4. Сравниваем хэши
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=401, detail="Invalid Telegram signature. Hacker detected!")

    # Достаем JSON с данными юзера
    user_json = data_dict.get('user', '{}')
    return json.loads(user_json)


async def get_current_player(
    authorization: str = Header(..., description="tghash <init_data>"),
    player_repo: PlayerRepository = Depends(get_player_repo) # Инжектим ниже
) -> Player:
    """FastAPI зависимость, которая автоматически достает текущего игрока"""
    
    # Фронтенд будет слать заголовок: "Authorization: tghash user=%7B...%7D&auth_date=..."
    if not authorization.startswith("tghash "):
         raise HTTPException(status_code=401, detail="Invalid authorization scheme")
         
    init_data = authorization.replace("tghash ", "")
    
    # Проверяем криптографию
    user_data = verify_telegram_signature(init_data)
    telegram_id = user_data.get("id")
    username = user_data.get("username") or user_data.get("first_name") or f"user_{telegram_id}"
    
    if not telegram_id:
        raise HTTPException(status_code=401, detail="User ID not found in init data")

    # Ищем игрока в базе
    player = await player_repo.get_by_telegram_id(int(telegram_id))
    if not player:
        # 🎉 АВТО-РЕГИСТРАЦИЯ: Создаем игрока при первом входе!
        from uuid import uuid4
        from app.domain.entities.player import Player
        
        player = Player(
            id=uuid4(),
            telegram_id=telegram_id,
            username=username,
            xp=0,
            daily_streak=0,
            xgen_balance=100,  # Стартовый капитал для нового игрока
            fragments_balance=50,
            ships=[]           # Пока без корабля
        )
        await player_repo.save(player)
        
    return player