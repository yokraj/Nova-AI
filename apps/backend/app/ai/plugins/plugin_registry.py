"""Plugin Registry storing registered plugin specs and active instances."""

from typing import Dict, List, Optional
import structlog

from app.ai.plugins.exceptions import PluginNotFoundError
from app.ai.plugins.interfaces import IPluginRegistry
from app.ai.plugins.models import PluginSpec, PluginStatus

logger = structlog.get_logger("plugin_registry")


class PluginRegistry(IPluginRegistry):
    """In-memory registry managing installed plugin specifications and instances."""

    def __init__(self) -> None:
        self._specs: Dict[str, PluginSpec] = {}
        self._instances: Dict[str, Any] = {}

    def add_plugin(self, spec: PluginSpec, instance: Optional[Any] = None) -> None:
        """Register or update a plugin spec."""
        self._specs[spec.plugin_id] = spec
        if instance is not None:
            self._instances[spec.plugin_id] = instance
        logger.debug("Registered plugin", plugin_id=spec.plugin_id, status=spec.status.value)

    def remove_plugin(self, plugin_id: str) -> bool:
        """Remove a plugin from the registry."""
        existed = plugin_id in self._specs
        self._specs.pop(plugin_id, None)
        self._instances.pop(plugin_id, None)
        return existed

    def get_plugin(self, plugin_id: str) -> Optional[PluginSpec]:
        """Retrieve plugin spec by ID."""
        return self._specs.get(plugin_id)

    def get_instance(self, plugin_id: str) -> Optional[Any]:
        """Retrieve plugin class instance by ID."""
        return self._instances.get(plugin_id)

    def list_plugins(self) -> List[PluginSpec]:
        """Return all registered plugins."""
        return list(self._specs.values())

    def update_status(self, plugin_id: str, status: PluginStatus, error: Optional[str] = None) -> None:
        """Update a plugin's lifecycle status."""
        spec = self._specs.get(plugin_id)
        if not spec:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' not found in registry.")
        spec.status = status
        if error:
            spec.error_message = error
        logger.info("Updated plugin status", plugin_id=plugin_id, status=status.value)

    def count(self) -> int:
        """Total number of registered plugins."""
        return len(self._specs)

    def clear(self) -> None:
        """Clear all registered plugins."""
        self._specs.clear()
        self._instances.clear()


from typing import Any  # noqa: E402
