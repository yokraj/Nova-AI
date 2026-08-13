"""Unified static locator for dynamic dependency lookups.
"""

from typing import Any
from app.ai.agents.dependency_container import DependencyContainer

class ServiceLocator:
    """Wrapper exposing static container resolution APIs."""

    _container = DependencyContainer()

    @classmethod
    def get_container(cls) -> DependencyContainer:
        """Returns the global DependencyContainer instance."""
        return cls._container

    @classmethod
    def resolve(cls, name: str) -> Any:
        """Resolves target service statically from global container."""
        return cls._container.resolve(name)
