"""Mock Automation Provider simulating desktop and browser automation deterministically."""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger("mock_provider")


class MockBrowserDriver:
    """Mock web driver simulating browser actions."""

    def __init__(self) -> None:
        self.logs: List[str] = []

    async def open_url(self, url: str) -> None:
        self.logs.append(f"open_url: {url}")

    async def navigate(self, url: str) -> None:
        self.logs.append(f"navigate: {url}")

    async def click_element(self, selector: str) -> None:
        self.logs.append(f"click: {selector}")

    async def fill_input(self, selector: str, value: str) -> None:
        self.logs.append(f"fill: {selector}={value}")

    async def screenshot(self, path: str) -> None:
        self.logs.append(f"screenshot: {path}")

    async def refresh(self) -> None:
        self.logs.append("refresh")

    async def back(self) -> None:
        self.logs.append("back")

    async def forward(self) -> None:
        self.logs.append("forward")


class MockAutomationProvider:
    """Deterministic offline mock provider for desktop & browser automation."""

    def __init__(self) -> None:
        self.browser = MockBrowserDriver()
        self.execution_logs: List[Dict[str, Any]] = []

    async def execute_action(self, action_type: str, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simulated automation action."""
        record = {"type": action_type, "name": action_name, "params": parameters}
        self.execution_logs.append(record)
        logger.info("MockAutomationProvider executed action", type=action_type, name=action_name)
        return {"status": "success", "result": record}
