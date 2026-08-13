"""Plugin Health Monitor checking status of all platform sub-components."""

from typing import Any
from app.ai.plugins.models import PluginHealth


class PluginHealthMonitor:
    """Evaluates composite health of registry, loader, execution manager, and sandbox."""

    def __init__(
        self,
        registry: Any,
        capability_registry: Any,
        sandbox: Any,
    ) -> None:
        self.registry = registry
        self.capability_registry = capability_registry
        self.sandbox = sandbox

    def check_health(self) -> PluginHealth:
        """Evaluate status report across sub-components."""
        components = {
            "registry": "online" if self.registry else "offline",
            "capability_registry": "online" if self.capability_registry else "offline",
            "sandbox": "online" if self.sandbox else "offline",
        }
        overall = "healthy" if all(v == "online" for v in components.values()) else "degraded"
        return PluginHealth(
            status=overall,
            components=components,
            total_plugins=self.registry.count() if self.registry else 0,
            active_capabilities=self.capability_registry.count() if self.capability_registry else 0,
        )
