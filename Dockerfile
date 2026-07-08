FROM python:3.11-slim

WORKDIR /app

# Системные зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock* ./

# Устанавливаем зависимости
RUN uv sync --frozen || uv sync

# Копируем исходный код
COPY src/ ./src/

# ⬇️ ДОБАВЛЕНО: Копируем миграции и конфиг Alembic
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Диагностические скрипты
COPY check_expeditions.py ./
COPY fix_stuck_expeditions.py ./

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]