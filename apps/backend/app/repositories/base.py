"""Generic database repository abstract base for Nova AI.

Defines the BaseRepository offering generic CRUD wrappers for database models
working with asynchronous SQLAlchemy sessions.
"""

from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async repository providing standard CRUD database operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        """Initializes the repository with model type and session dependency.

        Args:
            model: The SQLAlchemy model class type.
            session: An active SQLAlchemy AsyncSession instance.
        """
        self.model = model
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        """Retrieves a single model record by its primary key identifier.

        Args:
            id: The primary key identifier.

        Returns:
            The matched model instance, or None if not found.
        """
        return await self.session.get(self.model, id)

    async def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Lists records from the database with offset pagination.

        Args:
            skip: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of model instances.
        """
        statement = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        """Saves a new record instance into the database session tracker.

        Args:
            entity: The model object instance to add.

        Returns:
            The added model object instance.
        """
        self.session.add(entity)
        return entity

    async def delete(self, id: Any) -> Optional[ModelType]:
        """Deletes a database record matching the primary key identifier.

        Args:
            id: The primary key identifier.

        Returns:
            The deleted model object instance, or None if not found.
        """
        entity = await self.get(id)
        if entity:
            await self.session.delete(entity)
        return entity
