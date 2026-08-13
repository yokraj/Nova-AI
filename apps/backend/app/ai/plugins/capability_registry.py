"""Capability Registry mapping capability names to host plugins and handlers."""

from typing import Dict, List, Optional, Tuple
import structlog

from app.ai.plugins.models import PluginCapability

logger = structlog.get_logger("capability_registry")


class CapabilityRegistry:
    """Registry maintaining capability lookup maps across all enabled plugins."""

    def __init__(self) -> None:
        # (plugin_id, capability_name) -> PluginCapability
        self._capabilities: Dict[Tuple[str, str], PluginCapability] = {}

    def register_capability(self, plugin_id: str, capability: PluginCapability) -> None:
        """Register a single capability under a plugin."""
        key = (plugin_id, capability.name.lower())
        self._capabilities[key] = capability
        logger.debug("Registered capability", plugin_id=plugin_id, capability=capability.name)

    def unregister_plugin_capabilities(self, plugin_id: str) -> None:
        """Remove all capabilities associated with a plugin."""
        keys_to_remove = [k for k in self._capabilities if k[0] == plugin_id]
        for key in keys_to_remove:
            self._capabilities.pop(key, None)

    def find_capability(self, capability_name: str, plugin_id: str = "") -> Optional[Tuple[str, PluginCapability]]:
        """Look up a capability by name, optionally filtered by plugin_id."""
        cap_lower = capability_name.lower()
        if plugin_id:
            key = (plugin_id, cap_lower)
            cap = self._capabilities.get(key)
            return (plugin_id, cap) if cap else None

        # Search across all registered capabilities
        for (pid, cname), cap in self._capabilities.items():
            if cname == cap_lower:
                return (pid, cap)
        return None

    def list_capabilities(self, plugin_id: str = "") -> List[PluginCapability]:
        """List all registered capabilities, optionally filtered by plugin_id."""
        if plugin_id:
            return [cap for (pid, _), cap in self._capabilities.items() if pid == plugin_id]
        return list(self._capabilities.values())

    def count(self) -> int:
        """Total registered capabilities."""
        return len(self._capabilities)

    def clear(self) -> None:
        """Clear capability registry."""
        self._capabilities.clear()
