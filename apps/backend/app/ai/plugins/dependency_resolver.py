"""Dependency Resolver ensuring inter-plugin dependencies are satisfied."""

from typing import Dict, List
import structlog

from app.ai.plugins.exceptions import DependencyError
from app.ai.plugins.models import PluginSpec

logger = structlog.get_logger("dependency_resolver")


class DependencyResolver:
    """Resolves and validates inter-plugin dependencies."""

    def resolve_dependencies(self, spec: PluginSpec, available_plugins: Dict[str, PluginSpec]) -> List[str]:
        """Check if all declared dependencies exist in available_plugins."""
        missing = []
        for dep in spec.metadata.dependencies:
            if dep not in available_plugins:
                missing.append(dep)

        if missing:
            raise DependencyError(
                f"Plugin '{spec.plugin_id}' has missing dependencies: {', '.join(missing)}"
            )

        logger.debug("Resolved dependencies", plugin_id=spec.plugin_id, deps=spec.metadata.dependencies)
        return spec.metadata.dependencies
