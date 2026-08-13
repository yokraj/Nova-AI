"""Browser Sessions managing cookies, history, credentials, profiles, and incognito sessions.
"""

from typing import Any, Dict, List
from app.ai.desktop_automation.models import BrowserSession


class BrowserSessions:
    """Manages browser user profiles, cookie persistence, credentials, and incognito sessions."""

    def create_session(self, browser_name: str = "chrome", is_incognito: bool = False) -> BrowserSession:
        """Creates browser session instance."""
        return BrowserSession(
            browser_name=browser_name,
            is_incognito=is_incognito,
            profile_path=f"./data/browser_profiles/{browser_name}_default",
        )
