import json
import logging
from datetime import datetime, timezone

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class NotificationQueue:
    """Redis-backed notification queue with dead letter support."""

    QUEUE_KEY = "notifications:pending"
    DLQ_KEY = "notifications:dead_letter"
    MAX_RETRIES = 3

    def __init__(self, redis: Redis):
        self.redis = redis

    async def enqueue(self, chat_id: int, text: str, retry_count: int = 0) -> None:
        """Add notification to the pending queue."""
        notification = {
            "chat_id": chat_id,
            "text": text,
            "retry_count": retry_count,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.redis.lpush(self.QUEUE_KEY, json.dumps(notification))
        logger.info(f"Enqueued notification for chat_id={chat_id} (retry={retry_count})")

    async def dequeue(self) -> dict | None:
        """Remove and return one notification from the queue."""
        raw = await self.redis.rpop(self.QUEUE_KEY)
        if raw is None:
            return None
        return json.loads(str(raw))

    async def move_to_dlq(self, notification: dict) -> None:
        """Move permanently failed notification to dead letter queue."""
        await self.redis.lpush(self.DLQ_KEY, json.dumps(notification))
        logger.warning(f"Moved to DLQ: chat_id={notification.get('chat_id')}")

    async def queue_length(self) -> int:
        """Return current queue length."""
        return await self.redis.llen(self.QUEUE_KEY)

    async def dlq_length(self) -> int:
        """Return dead letter queue length."""
        return await self.redis.llen(self.DLQ_KEY)
