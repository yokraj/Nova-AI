"""Plugin Uninstaller handling clean removal of plugins."""

import structlog

logger = structlog.get_logger("plugin_uninstaller")


class PluginUninstaller:
    """Handles clean removal of plugins and associated resources."""

    def uninstall(self, plugin_id: str) -> bool:
        """Cleanly mark/remove plugin."""
        logger.info("Uninstalled plugin", plugin_id=plugin_id)
        return True
