from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # App
    APP_NAME: str = "Hitchhiker's Idle Strategy"
    DEBUG: bool = False

    # Database - новая опция (читается из DATABASE_URL в Coolify)
    DATABASE_URL: str | None = Field(default=None, alias="DATABASE_URL")

    # Fallback значения (для локальной разработки)
    POSTGRES_USER: str = "vogon"
    POSTGRES_PASSWORD: str = "poetry_is_bad"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5435
    POSTGRES_DB: str = "galaxy_db"

    @property
    def database_url(self) -> str:
        # Если DATABASE_URL передан через окружение (Coolify) - используем его
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Иначе собираем из компонентов (для локальной разработки)
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "https://app.exo-gen.com",
        "https://telegram.org",
    ]

    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 20

    # Telegram auth
    TELEGRAM_AUTH_MAX_AGE_SECONDS: int = 86400  # 24 часа

    # Telegram
    ADMIN_TELEGRAM_IDS: list[int] = []
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token from BotFather")

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6381

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6381/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6381/2"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()