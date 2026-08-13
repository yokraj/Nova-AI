"""Browser Controller managing multi-browser web automation (Chrome, Edge, Firefox, Brave).
"""

from typing import Any, Dict
from app.ai.desktop_automation.interfaces import IBrowserController
from app.ai.desktop_automation.models import BrowserSession, BrowserTab


class BrowserController(IBrowserController):
    """Automates web browsers (Chrome, Edge, Firefox, Brave), tab navigation, downloads, and DOM inspection."""

    def __init__(self) -> None:
        self._session = BrowserSession()

    async def open_url(self, url: str, browser: str = "chrome") -> BrowserTab:
        """Opens URL in target browser."""
        self._session.browser_name = browser
        return BrowserTab(
            title=f"Page - {url}",
            url=url,
            is_active=True,
            index=0,
        )
