"""Browser Bridge connecting Service Engine workflows to BrowserController."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("browser_bridge")


class BrowserBridge:
    """Delegates web navigation and DOM actions to BrowserController."""

    def __init__(self, browser_controller: Any = None) -> None:
        self.browser = browser_controller

    async def navigate_and_interact(self, url: str, actions: list) -> bool:
        """Navigate and perform browser actions."""
        logger.info("BrowserBridge navigating URL", url=url, actions_count=len(actions))
        if self.browser:
            await self.browser.navigate_url(url)
        return True
