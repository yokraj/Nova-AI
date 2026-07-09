"""Alembic migrations environment setup.

Configures connection settings and maps application metadata base
to support async database schema auto-generation.
"""

from typing import Any
import asyncio
from logging.config import fileConfig

from alembic import context

from app.database.base import Base
from app.database.session import engine
from app.database.models import (
    User,
    RefreshToken,
    Conversation,
    Message,
    Session,
    UserPreference,
    AIProviderConfiguration,
)

# Retrieve Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set model metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures migration context with just a URL without active connection.
    """
    # Use fallback or config url. Since offline doesn't connect, url string is enough.
    url = engine.url.render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Any) -> None:
    """Invokes the migration scripts within the transaction block context."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Runs database migrations asynchronously using the active engine."""
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Run async function using asyncio event loop
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
