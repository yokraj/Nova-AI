"""Cookie Manager inspecting, setting, and clearing browser session cookies."""

from typing import Dict, List
import structlog

logger = structlog.get_logger("cookie_manager")


class CookieManager:
    """Manages browser session cookies."""

    def __init__(self) -> None:
        self._cookies: List[Dict[str, str]] = []

    async def get_cookies(self) -> List[Dict[str, str]]:
        """List active cookies."""
        return list(self._cookies)

    async def set_cookie(self, name: str, value: str, domain: str = "localhost") -> bool:
        """Set cookie."""
        self._cookies.append({"name": name, "value": value, "domain": domain})
        logger.info("Set browser cookie", name=name, domain=domain)
        return True

    async def clear_cookies(self) -> None:
        """Clear cookies."""
        self._cookies.clear()
        logger.info("Cleared browser cookies")
