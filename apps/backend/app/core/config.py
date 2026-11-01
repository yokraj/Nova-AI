"""Configuration management for Nova AI.

Loads, validates, and stores application settings from environment variables
using Pydantic Settings.
"""

from pathlib import Path
from typing import Any, List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.version import APP_NAME, VERSION

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # apps/backend
ROOT_DIR = BASE_DIR.parent.parent  # C:\Projects\Nova-AI

DEFAULT_DEV_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


class Settings(BaseSettings):
    """Application settings class supporting environment variable injection."""

    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), str(BASE_DIR / ".env"), ".env"),
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

    # AI Gateway Settings
    AI_DEFAULT_MODEL: str = "qwen3:8b"
    AI_MAX_RETRIES: int = 3
    AI_TIMEOUT_SECONDS: float = 60.0

    # Future Provider API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # CORS Origins Settings
    BACKEND_CORS_ORIGINS: Union[List[str], str] = Field(
        default_factory=lambda: list(DEFAULT_DEV_CORS_ORIGINS)
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """Parses a comma-separated string, JSON string, or a list of origins into a list."""
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                import json
                try:
                    parsed = json.loads(v_stripped)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            origins = [i.strip() for i in v.split(",") if i.strip()]
            return origins if origins else list(DEFAULT_DEV_CORS_ORIGINS)
        elif isinstance(v, (list, tuple, set)):
            origins = [str(i).strip() for i in v if str(i).strip()]
            return origins if origins else list(DEFAULT_DEV_CORS_ORIGINS)
        return list(DEFAULT_DEV_CORS_ORIGINS)

    # SQLite Database Fallback Path
    SQLITE_DB_PATH: str = Field(default_factory=lambda: str(ROOT_DIR / "data" / "nova_ai.db"))
    USE_SQLITE_FALLBACK: bool = True

    @field_validator("SQLITE_DB_PATH", mode="after")
    @classmethod
    def resolve_sqlite_path(cls, v: str) -> str:
        """Ensures SQLite path is always anchored against ROOT_DIR if relative."""
        p = Path(v)
        if not p.is_absolute():
            p = (ROOT_DIR / p).resolve()
        return str(p)

    @property
    def get_database_url(self) -> str:
        """Constructs or returns the async PostgreSQL or SQLite connection URL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.USE_SQLITE_FALLBACK:
            db_path = Path(self.SQLITE_DB_PATH)
            if not db_path.is_absolute():
                db_path = (ROOT_DIR / db_path).resolve()
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{db_path.as_posix()}"
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Instantiate settings globally for dependency injection and importing
settings = Settings()
