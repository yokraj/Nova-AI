"""Database session configuration and initialization for Nova AI.

Exposes connection setup, engine initialization, session maker, and the
get_db async generator dependency used in FastAPI path operators.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# Create the async engine with robust connection pooling and configurable query logging
engine = create_async_engine(
    settings.get_database_url,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
)

# Asynchronous session factory configured for automatic cleanup and transactions
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields a database session and handles transaction cleanup.

    Yields:
        An active SQLAlchemy AsyncSession.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
