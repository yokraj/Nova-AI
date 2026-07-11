"""Provider Registry tracking active AI provider adapters and health.
"""

from typing import Any, Dict, List, Optional
from app.ai.models import ProviderCapability, ProviderHealth


class ProviderRegistry:
    """Tracks active provider implementations adapters and health statuses."""

    def __init__(self) -> None:
        """Initializes ProviderRegistry."""
        self._providers: Dict[str, Any] = {}
        self._health: Dict[str, ProviderHealth] = {}

    def register(self, name: str, provider: Any) -> None:
        """Registers an active provider instance.

        Args:
            name: Provider name identifier.
            provider: Concrete provider adapter.
        """
        self._providers[name] = provider
        self._health[name] = ProviderHealth(is_healthy=True)

    def unregister(self, name: str) -> None:
        """Removes a provider adapter registration.

        Args:
            name: Provider identifier.
        """
        self._providers.pop(name, None)
        self._health.pop(name, None)

    def provider(self, name: str) -> Optional[Any]:
        """Fetches a registered provider instance by name.

        Args:
            name: Provider identifier.

        Returns:
            Provider instance, or None.
        """
        return self._providers.get(name)

    def list(self) -> List[str]:
        """Returns a list of all registered provider names.

        Returns:
            List of registered provider identifiers.
        """
        return list(self._providers.keys())

    def health(self, name: str) -> Optional[ProviderHealth]:
        """Retrieves health status details for a provider.

        Args:
            name: Provider identifier.

        Returns:
            ProviderHealth snapshot model, or None.
        """
        return self._health.get(name)

    def capabilities(self, name: str) -> List[ProviderCapability]:
        """Returns capabilities supported by a provider.

        Args:
            name: Provider name.

        Returns:
            List of capabilities supported.
        """
        provider = self.provider(name)
        if not provider:
            return []

        # If provider exposes available_models list, extract all capabilities
        if hasattr(provider, "available_models"):
            try:
                # Synchronous check if available_models is not async in mock classes
                import inspect
                if inspect.iscoroutinefunction(provider.available_models):
                    # We cannot await inside this sync method, fallback to base checks
                    pass
                else:
                    caps = set()
                    for model in provider.available_models():
                        caps.update(model.capabilities)
                    return list(caps)
            except Exception:
                pass

        # Standard fallbacks based on implemented interfaces
        from app.ai.shared import providerValidator
        supported = []
        for cap in ProviderCapability:
            if providerValidator.validate(provider, cap):
                supported.append(cap)
        return supported
