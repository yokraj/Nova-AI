"""Plugin Installer for installing plugins into the local system."""

import os
from typing import Optional
import structlog

from app.ai.plugins.configuration import PluginConfiguration
from app.ai.plugins.models import PluginMetadata, PluginSpec, PluginStatus

logger = structlog.get_logger("plugin_installer")


class PluginInstaller:
    """Handles plugin installation from file paths or specification objects."""

    def __init__(self, config: Optional[PluginConfiguration] = None) -> None:
        self.config = config or PluginConfiguration()

    def install(self, plugin_path_or_id: str) -> PluginSpec:
        """Install a plugin by creating spec or registering entrypoint."""
        plugin_id = os.path.basename(plugin_path_or_id).replace(".py", "").lower()
        spec = PluginSpec(
            plugin_id=plugin_id,
            metadata=PluginMetadata(
                name=plugin_id.title(),
                version="1.0.0",
                description=f"Installed plugin from {plugin_path_or_id}",
            ),
            entrypoint=plugin_path_or_id if os.path.exists(plugin_path_or_id) else "",
            status=PluginStatus.INSTALLED,
        )
        logger.info("Installed plugin", plugin_id=plugin_id, path=plugin_path_or_id)
        return spec
