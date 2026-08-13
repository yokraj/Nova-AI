"""Browser Profiles managing browser user profile settings and options."""

from typing import Dict, Any
import structlog

logger = structlog.get_logger("browser_profiles")


class BrowserProfiles:
    """Manages browser profiles, user data directories, and preferences."""

    def __init__(self) -> None:
        self._profiles: Dict[str, Dict[str, Any]] = {
            "default": {"user_data_dir": "./data/browser_profiles/default", "headless": False},
        }

    def get_profile(self, name: str = "default") -> Dict[str, Any]:
        """Get browser profile options."""
        return self._profiles.get(name, self._profiles["default"])
