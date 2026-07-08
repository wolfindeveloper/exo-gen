import asyncio
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.app.config.settings import settings

ZONE_ID = "2921de82-b14f-4b10-a1bb-965439073403"

RED = "\033[91m"
RESET = "\033[0m"


async def main():
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.connect() as conn:
        rows = await conn.execute(
            text("""
                SELECT id, status, started_at, ends_at
                FROM expeditions
                WHERE zone_id = :zone_id
                ORDER BY started_at DESC
            """),
            {"zone_id": ZONE_ID},
        )
        results = rows.fetchall()

    if not results:
        print(f"Нет экспедиций для зоны {ZONE_ID}")
        return

    now = datetime.now(timezone.utc)
    print(f"{'ID':<40} {'Status':<20} {'started_at':<30} {'ends_at':<30} {'current_time':<30}  Stuck?")
    print("-" * 155)

    for row in results:
        id_, status, started_at, ends_at = row
        end = ends_at.replace(tzinfo=timezone.utc) if ends_at.tzinfo is None else ends_at
        stuck = end < now and status.lower() not in ("completed", "finished", "claimed")

        line = f"{str(id_):<40} {status:<20} {str(started_at):<30} {str(ends_at):<30} {str(now):<30}"
        if stuck:
            print(f"{RED}{line}  ЭКСПЕДИЦИЯ ЗАВЕРШЕНА, НО НЕ ОБРАБОТАНА{RESET}")
        else:
            print(line)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
