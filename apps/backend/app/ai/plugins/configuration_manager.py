"""Configuration Manager storing plugin-specific runtime configurations."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("configuration_manager")


class ConfigurationManager:
    """Manages plugin configuration overrides and defaults."""

    def __init__(self) -> None:
        self._configs: Dict[str, Dict[str, Any]] = {}

    def set_config(self, plugin_id: str, config: Dict[str, Any]) -> None:
        """Set custom config for a plugin."""
        self._configs[plugin_id] = config
        logger.debug("Set plugin config", plugin_id=plugin_id)

    def get_config(self, plugin_id: str) -> Dict[str, Any]:
        """Get custom config for a plugin."""
        return self._configs.get(plugin_id, {})
