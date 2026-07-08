"""Configuration management for Nova AI.

Loads, validates, and stores application settings from environment variables
using Pydantic Settings.
"""

from typing import Any, List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.version import APP_NAME, VERSION


class Settings(BaseSettings):
    """Application settings class supporting environment variable injection."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # General App Metadata
    PROJECT_NAME: str = APP_NAME
    VERSION: str = VERSION
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # PostgreSQL Database Connection Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "nova_ai"
    DATABASE_URL: Union[str, None] = None
    DB_ECHO: bool = False

    # CORS Origins Settings
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=list)

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """Parses a comma-separated string or a list of origins into a list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    @property
    def get_database_url(self) -> str:
        """Constructs or returns the async PostgreSQL connection URL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Instantiate settings globally for dependency injection and importing
settings = Settings()
