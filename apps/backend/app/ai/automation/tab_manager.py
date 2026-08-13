"""Tab Manager managing browser tabs (new, close, switch, list)."""

from typing import Dict, List
import structlog

logger = structlog.get_logger("tab_manager")


class TabManager:
    """Manages multi-tab browser context state."""

    def __init__(self) -> None:
        self._tabs: List[Dict[str, str]] = [
            {"tab_id": "tab_1", "title": "New Tab", "url": "about:blank"},
        ]
        self._active_tab_id: str = "tab_1"

    async def create_tab(self, url: str = "about:blank") -> Dict[str, str]:
        """Open new tab."""
        tab_id = f"tab_{len(self._tabs) + 1}"
        tab = {"tab_id": tab_id, "title": "Page", "url": url}
        self._tabs.append(tab)
        self._active_tab_id = tab_id
        logger.info("Created browser tab", tab_id=tab_id, url=url)
        return tab

    async def close_tab(self, tab_id: str) -> bool:
        """Close specified browser tab."""
        self._tabs = [t for t in self._tabs if t["tab_id"] != tab_id]
        if self._tabs:
            self._active_tab_id = self._tabs[-1]["tab_id"]
        logger.info("Closed browser tab", tab_id=tab_id)
        return True

    async def switch_tab(self, tab_id: str) -> Dict[str, str]:
        """Switch active tab."""
        for t in self._tabs:
            if t["tab_id"] == tab_id:
                self._active_tab_id = tab_id
                logger.info("Switched active browser tab", tab_id=tab_id)
                return t
        raise ValueError(f"Tab '{tab_id}' not found.")

    async def list_tabs(self) -> List[Dict[str, str]]:
        """List active tabs."""
        return list(self._tabs)
