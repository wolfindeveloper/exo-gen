FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv (быстрый менеджер пакетов)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock* ./

# Устанавливаем зависимости (если есть uv.lock — используем его, иначе создаём)
RUN uv sync --frozen || uv sync

# Копируем исходный код
COPY src/ ./src/

# Открываем порт
EXPOSE 8000

# Запускаем приложение через uv
CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]