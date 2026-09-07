"""Database session configuration and initialization for Nova AI.

Exposes connection setup, engine initialization, session maker, and the
get_db async generator dependency used in FastAPI path operators.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

db_url = settings.get_database_url
engine_kwargs = {
    "echo": settings.DB_ECHO,
}
if not db_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 10,
    })

# Create the async engine with connection options
engine = create_async_engine(db_url, **engine_kwargs)

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
