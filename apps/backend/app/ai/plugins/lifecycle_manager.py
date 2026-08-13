"""Lifecycle Manager orchestrating plugin state transitions."""

from typing import Optional
import structlog

from app.ai.plugins.exceptions import PluginNotFoundError
from app.ai.plugins.models import PluginSpec, PluginStatus
from app.ai.plugins.plugin_registry import PluginRegistry

logger = structlog.get_logger("lifecycle_manager")


class LifecycleManager:
    """Manages state transitions: INSTALLED -> LOADED -> ENABLED -> DISABLED -> UNINSTALLED."""

    def __init__(self, registry: Optional[PluginRegistry] = None) -> None:
        self.registry = registry or PluginRegistry()

    def transition(self, plugin_id: str, target_status: PluginStatus) -> PluginSpec:
        """Enforce valid state transition for a plugin."""
        spec = self.registry.get_plugin(plugin_id)
        if not spec:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' not found.")

        old_status = spec.status
        spec.status = target_status
        logger.info(
            "Lifecycle status transition",
            plugin_id=plugin_id,
            from_status=old_status.value,
            to_status=target_status.value,
        )
        return spec
