"""Application settings loaded from environment variables."""

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for EXO GENESIS backend.

    All values are read from environment variables or .env file.
    Defaults are safe for local development only.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = Field(default="development", description="Runtime environment")
    app_debug: bool = Field(default=True, description="Enable debug mode")
    app_host: str = Field(default="0.0.0.0", description="HTTP bind address")
    app_port: int = Field(default=8000, description="HTTP bind port")

    secret_key: str = Field(
        default="change-me-to-random-string",
        alias="JWT_SECRET",
        description="Master secret for JWT signing",
    )

    telegram_bot_token: str = Field(
        default="",
        description="Telegram Bot API token from @BotFather",
    )
    telegram_secret_key: str = Field(
        default="",
        description="Telegram Web App secret key for initData validation",
    )
    telegram_bot_username: str = Field(
        default="",
        description="Telegram bot username (without @)",
    )

    world_id_app_id: str = Field(
        default="",
        alias="WORLDCOIN_APP_ID",
        description="World ID (Worldcoin) application identifier",
    )
    world_id_client_secret: str = Field(
        default="",
        description="World ID client secret for verification",
    )

    postgres_user: str = Field(
        default="exo_user",
        description="PostgreSQL username",
    )
    postgres_password: str = Field(
        default="exo_password",
        description="PostgreSQL password",
    )
    postgres_db: str = Field(
        default="exo_genesis",
        description="PostgreSQL database name",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://exo_user:exo_password@localhost:5432/exo_genesis",
        description="Async SQLAlchemy connection string",
    )
    database_url_sync: str = Field(
        default="postgresql://exo_user:exo_password@localhost:5432/exo_genesis",
        description="Synchronous connection string for Alembic",
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_cache_ttl: int = Field(
        default=3600,
        description="Default TTL in seconds for cached configs",
    )

    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Redis URL for Celery broker",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="Redis URL for Celery result backend",
    )

    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_expire_minutes: int = Field(
        default=1440,
        description="JWT token lifetime in minutes",
    )
    jwt_expire_hours: int = Field(
        default=24,
        description="JWT token lifetime in hours (convenience)",
    )

    @computed_field
    @property
    def jwt_expire_hours_computed(self) -> float:
        """JWT expiration converted to hours."""
        return self.jwt_expire_minutes / 60

    rate_limit_per_minute: int = Field(
        default=60,
        description="Max requests per minute per client",
    )

    ton_network: str = Field(
        default="testnet",
        description="TON network: testnet | mainnet",
    )
    ton_api_key: str = Field(
        default="",
        description="TON Center API key",
    )
    xgen_minter_address: str = Field(
        default="",
        description="XGEN Jetton minter contract address",
    )


settings = Settings()
