"""Dependency Injection Container managing transient and singleton services.
"""

import structlog
from typing import Any, Callable, Dict

from app.ai.agents.exceptions import AgentDependencyError

logger = structlog.get_logger("dependency_container")

class DependencyContainer:
    """Maintains service factory registrations and active instances scopes."""

    def __init__(self) -> None:
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._instances: Dict[str, Any] = {}

    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        """Registers a singleton service factory."""
        self._registry[name] = {"lifetime": "singleton", "factory": factory}

    def register_transient(self, name: str, factory: Callable[[], Any]) -> None:
        """Registers a transient service factory."""
        self._registry[name] = {"lifetime": "transient", "factory": factory}

    def register_instance(self, name: str, instance: Any) -> None:
        """Registers an already instantiated object as a singleton."""
        self._registry[name] = {"lifetime": "singleton", "factory": lambda: instance}
        self._instances[name] = instance

    def resolve(self, name: str) -> Any:
        """Resolves target service by name, executing factories or returning singletons."""
        if name in self._instances:
            return self._instances[name]

        registration = self._registry.get(name)
        if not registration:
            raise AgentDependencyError(f"Dependency '{name}' could not be resolved (no registration found).")

        factory = registration["factory"]
        lifetime = registration["lifetime"]

        if lifetime == "singleton":
            instance = factory()
            self._instances[name] = instance
            return instance
        
        return factory()

    def clear(self) -> None:
        """Purges registrations and cached instances."""
        self._registry.clear()
        self._instances.clear()
