"""Version Manager handling semantic version checking and compatibility."""

from typing import Tuple
import structlog

from app.ai.plugins.models import PluginMetadata

logger = structlog.get_logger("version_manager")


class VersionManager:
    """Handles semver comparison and Nova core compatibility validation."""

    NOVA_VERSION = "3.0.0"

    def is_compatible(self, metadata: PluginMetadata) -> bool:
        """Check if plugin's min_nova_version is compatible with current Nova core version."""
        try:
            req = self._parse_version(metadata.min_nova_version)
            cur = self._parse_version(self.NOVA_VERSION)
            return cur >= req
        except Exception as err:
            logger.warning("Version parsing error", error=str(err))
            return True

    @staticmethod
    def _parse_version(v_str: str) -> Tuple[int, int, int]:
        parts = [int(x) for x in v_str.strip("v").split(".")[:3]]
        while len(parts) < 3:
            parts.append(0)
        return (parts[0], parts[1], parts[2])
