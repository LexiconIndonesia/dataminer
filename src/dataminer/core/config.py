"""Application configuration management."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Path | None:
    """Find .env file by walking up from current file to project root.

    Returns the path if found, None otherwise. Pydantic-settings handles
    the actual loading, ensuring system env vars take precedence over
    .env file values (standard 12-factor app behavior).
    """
    current = Path(__file__).resolve()
    # Walk up to find .env file (src/dataminer/core/config.py -> project root)
    for parent in [current, *current.parents]:
        env_file = parent / ".env"
        if env_file.exists():
            return env_file
    # No .env file found - rely on actual environment variables (production)
    return None


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(default="dataminer", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Environment"
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        alias="allowed_origins",
        description="Allowed CORS origins (comma-separated)",
    )

    @computed_field
    @property
    def allowed_origins(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]

    # Database Settings
    database_url: PostgresDsn = Field(
        default="postgresql://postgres:postgres@localhost:5432/dataminer",
        description="Database URL",
    )
    test_database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/dataminer_test",
        description="Test database URL (async)",
    )
    db_echo: bool = Field(default=False, description="Echo SQL queries")
    db_pool_size: int = Field(default=5, description="Database pool size")
    db_max_overflow: int = Field(default=10, description="Database max overflow")

    # Redis Settings
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0", description="Redis URL")
    redis_max_connections: int = Field(default=10, description="Redis max connections")

    # NATS Settings
    nats_url: str = Field(default="nats://localhost:4222", description="NATS URL")
    nats_stream_name: str = Field(default="dataminer", description="NATS stream name")
    nats_subject_prefix: str = Field(default="dataminer", description="NATS subject prefix")

    # Security
    secret_key: str = Field(default="change-this-secret-key", description="Secret key")
    api_key: str = Field(default="change-this-api-key", description="API key")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")

    # Processing Settings
    max_workers: int = Field(default=4, description="Max concurrent workers")
    job_timeout_seconds: int = Field(default=300, description="Job timeout in seconds")
    max_retries: int = Field(default=3, description="Max retries for failed jobs")

    # Cost Settings
    default_max_cost_per_document: float = Field(
        default=2.00, description="Default max cost per document"
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
