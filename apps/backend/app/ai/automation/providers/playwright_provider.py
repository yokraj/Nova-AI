"""Playwright Provider implements optional headless chromium automation routines.
"""

import structlog
from typing import Optional

logger = structlog.get_logger("playwright_provider")

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class PlaywrightBrowserProvider:
    """Wraps chromium web automation APIs, degrading gracefully if not installed."""

    def __init__(self) -> None:
        self.is_mock = not PLAYWRIGHT_AVAILABLE
        self._playwright_instance: Optional[Any] = None
        self._browser: Optional[Any] = None
        self._context: Optional[Any] = None
        self._page: Optional[Any] = None

    async def open_url(self, url: str) -> None:
        """Launches chromium headless browser and goes to the target URL."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright is not installed; skipping browser navigation")
            return

        try:
            if not self._playwright_instance:
                self._playwright_instance = await async_playwright().start()
                self._browser = await self._playwright_instance.chromium.launch(headless=True)
                self._context = await self._browser.new_context()
                self._page = await self._context.new_page()
            await self._page.goto(url)
        except Exception as err:
            logger.error("Playwright browser initialization failed", error=str(err))

    async def navigate(self, url: str) -> None:
        """Navigates active page to target URL."""
        if self._page:
            await self._page.goto(url)

    async def refresh(self) -> None:
        """Reloads active page tab."""
        if self._page:
            await self._page.reload()

    async def back(self) -> None:
        """Goes back in browser session history."""
        if self._page:
            await self._page.go_back()

    async def forward(self) -> None:
        """Goes forward in browser session history."""
        if self._page:
            await self._page.go_forward()

    async def click_element(self, selector: str) -> None:
        """Clicks target selector element."""
        if self._page:
            await self._page.click(selector)

    async def fill_input(self, selector: str, value: str) -> None:
        """Fills input target element with value."""
        if self._page:
            await self._page.fill(selector, value)

    async def screenshot(self, output_path: str) -> None:
        """Saves current viewport screen buffer image."""
        if self._page:
            await self._page.screenshot(path=output_path)

    async def extract_dom(self) -> str:
        """Retrieves raw HTML content of the page."""
        if self._page:
            return await self._page.content()
        return "<html><body>Playwright Mock Content</body></html>"

    async def close(self) -> None:
        """Shuts down active chromium instance context."""
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright_instance:
                await self._playwright_instance.stop()
        except Exception:
            pass
