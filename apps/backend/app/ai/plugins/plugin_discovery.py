"""Plugin Discovery scanning local directories for installable plugins."""

import os
from typing import List, Optional
import structlog

from app.ai.plugins.configuration import PluginConfiguration
from app.ai.plugins.models import PluginMetadata, PluginSpec, PluginStatus

logger = structlog.get_logger("plugin_discovery")


class PluginDiscovery:
    """Scans local filesystem directories to discover plugin packages."""

    def __init__(self, config: Optional[PluginConfiguration] = None) -> None:
        self.config = config or PluginConfiguration()

    def discover_plugins(self, target_dir: Optional[str] = None) -> List[PluginSpec]:
        """Scan directory for python plugin files or plugin folders."""
        scan_path = target_dir or self.config.plugins_dir
        discovered: List[PluginSpec] = []

        if not os.path.exists(scan_path):
            logger.debug("Plugin directory does not exist, creating", path=scan_path)
            try:
                os.makedirs(scan_path, exist_ok=True)
            except Exception:
                pass
            return []

        for item in os.listdir(scan_path):
            item_path = os.path.join(scan_path, item)
            if item.endswith(".py") and not item.startswith("__"):
                plugin_id = item[:-3].lower()
                spec = PluginSpec(
                    plugin_id=plugin_id,
                    metadata=PluginMetadata(name=item[:-3].title(), version="1.0.0"),
                    entrypoint=item_path,
                    status=PluginStatus.INSTALLED,
                )
                discovered.append(spec)
            elif os.path.isdir(item_path) and not item.startswith("__"):
                plugin_id = item.lower()
                spec = PluginSpec(
                    plugin_id=plugin_id,
                    metadata=PluginMetadata(name=item.title(), version="1.0.0"),
                    entrypoint=item_path,
                    status=PluginStatus.INSTALLED,
                )
                discovered.append(spec)

        logger.info("Discovered local plugins", count=len(discovered), directory=scan_path)
        return discovered
