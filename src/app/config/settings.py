from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Pydantic V2 config
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=False, 
        extra="ignore"
    )

    # App
    APP_NAME: str = "Hitchhiker's Idle Strategy"
    DEBUG: bool = False

    # Database (PostgreSQL 16)
    POSTGRES_USER: str = "vogon"
    POSTGRES_PASSWORD: str = "poetry_is_bad"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5435
    POSTGRES_DB: str = "galaxy_db"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

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