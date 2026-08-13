"""Plugin Validator enforcing manifest completeness and structural integrity."""

import structlog

from app.ai.plugins.exceptions import PluginValidationError
from app.ai.plugins.models import PluginSpec

logger = structlog.get_logger("plugin_validator")


class PluginValidator:
    """Validates plugin specifications before registration or loading."""

    def validate(self, spec: PluginSpec) -> bool:
        """Validate required fields in plugin spec."""
        if not spec.plugin_id or not spec.plugin_id.strip():
            raise PluginValidationError("Plugin spec missing required 'plugin_id'.")

        if not spec.metadata.name or not spec.metadata.name.strip():
            raise PluginValidationError(f"Plugin '{spec.plugin_id}' metadata missing 'name'.")

        if not spec.metadata.version:
            raise PluginValidationError(f"Plugin '{spec.plugin_id}' metadata missing 'version'.")

        logger.debug("Validated plugin spec", plugin_id=spec.plugin_id)
        return True
