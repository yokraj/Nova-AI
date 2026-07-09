"""Unit of Work (UoW) pattern implementation for Nova AI database operations.

Coordinates database transaction boundaries across repositories and services,
ensuring atomicity and automatic resource cleanup.
"""

from types import TracebackType
from typing import Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import SessionLocal


class UnitOfWork:
    """Manages transactional database boundaries using an async context manager."""

    def __init__(self) -> None:
        self._session_factory = SessionLocal
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self) -> "UnitOfWork":
        """Spawns a new active database session."""
        self.session = self._session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Closes the session, rolling back on error or committing on success."""
        if self.session:
            try:
                if exc_type is not None:
                    await self.rollback()
                else:
                    await self.commit()
            finally:
                await self.session.close()
                self.session = None

    async def commit(self) -> None:
        """Commits changes pending in the current session transaction."""
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        """Rolls back all uncommitted session operations."""
        if self.session:
            await self.session.rollback()
