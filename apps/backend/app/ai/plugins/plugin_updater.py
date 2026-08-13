"""Plugin Updater handling plugin updates and migrations."""

import structlog
from typing import Optional

from app.ai.plugins.models import PluginSpec

logger = structlog.get_logger("plugin_updater")


class PluginUpdater:
    """Handles updating installed plugin specifications to newer versions."""

    def update(self, current_spec: PluginSpec, new_version: str) -> PluginSpec:
        """Update plugin version metadata."""
        current_spec.metadata.version = new_version
        logger.info("Updated plugin version", plugin_id=current_spec.plugin_id, new_version=new_version)
        return current_spec
