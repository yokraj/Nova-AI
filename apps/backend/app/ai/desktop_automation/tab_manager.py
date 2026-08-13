"""Tab Manager managing browser tabs, activation, switching, and URL tracking.
"""

from typing import Any, Dict, List
from app.ai.desktop_automation.models import BrowserTab


class TabManager:
    """Manages browser tabs, tab creation, closing, and URL navigation tracking."""

    def __init__(self) -> None:
        self._tabs: List[BrowserTab] = [
            BrowserTab(title="Nova AI Dashboard", url="http://localhost:3000", is_active=True, index=0)
        ]

    def list_tabs(self) -> List[BrowserTab]:
        """Lists active browser tabs."""
        return list(self._tabs)

    def new_tab(self, url: str) -> BrowserTab:
        """Opens new browser tab."""
        tab = BrowserTab(title=f"Tab {len(self._tabs)+1}", url=url, is_active=True, index=len(self._tabs))
        self._tabs.append(tab)
        return tab
