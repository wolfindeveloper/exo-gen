import json

import redis.asyncio as redis

from app.config.settings import settings


class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> dict | None:
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: dict, ex: int = 300):
        await self.client.set(key, json.dumps(value), ex=ex)

    async def delete(self, key_pattern: str):
        cursor = 0
        while True:
            cursor, keys = await self.client.scan(cursor, match=key_pattern, count=100)
            if keys:
                await self.client.delete(*keys)
            if cursor == 0:
                break


redis_client = RedisClient()
