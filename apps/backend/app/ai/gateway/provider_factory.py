"""Provider Factory creating and validating AI provider adapters dynamically.
"""

from typing import Any, Dict, Type
from app.ai.gateway.exceptions import ProviderNotFoundError
from app.ai.gateway.provider_registry import ProviderRegistry
from app.ai.models import ProviderCapability
from app.ai.shared import providerValidator


class ProviderFactory:
    """Validates and constructs concrete provider adapters dynamically."""

    def __init__(self, registry: ProviderRegistry) -> None:
        """Initializes ProviderFactory.

        Args:
            registry: Active ProviderRegistry.
        """
        self.registry = registry
        self._lazy_loaders: Dict[str, Type[Any]] = {}

    def register_lazy(self, name: str, cls: Type[Any]) -> None:
        """Registers a loader definition for lazy provider construction.

        Args:
            name: Provider name identifier.
            cls: Concrete class type.
        """
        self._lazy_loaders[name] = cls

    def create(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Dynamically creates or returns a provider instance.

        Args:
            name: Provider name key.
            *args: Constructor arguments.
            **kwargs: Constructor keyword arguments.

        Returns:
            The provider adapter instance.
        """
        if name in self._lazy_loaders:
            cls = self._lazy_loaders[name]
            instance = cls(*args, **kwargs)
            self.registry.register(name, instance)
            return instance

        provider = self.registry.provider(name)
        if not provider:
            raise ProviderNotFoundError(f"Provider '{name}' definition is not registered.")
        return provider

    def validate_provider(self, provider: Any, capability: ProviderCapability) -> bool:
        """Checks if a provider implements the required capability contract.

        Args:
            provider: Provider instance to check.
            capability: Target capability enum.

        Returns:
            True if conforms; False otherwise.
        """
        return providerValidator.validate(provider, capability)
