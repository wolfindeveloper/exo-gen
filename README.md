# EXO GENESIS

TON-based Telegram Mini App game. Config-driven backend with FastAPI, PostgreSQL, Redis, and Celery.

## Quick Start

```bash
uv venv .venv
.venv\Scripts\activate
uv sync
uv run uvicorn api.main:app --reload
```

## Stack

- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.0 async
- **DB/Cache:** PostgreSQL 16, Redis 7
- **Tasks:** Celery + Redis
- **Package Manager:** uv
- **Blockchain:** TON, Tact (TEP-62/74)
