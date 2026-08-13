"""Mock Assistant Provider simulating assistant actions deterministically."""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger("assistant_mock_provider")


class MockAssistantProvider:
    """Deterministic offline provider for personal assistant engine testing."""

    def __init__(self) -> None:
        self.logs: List[Dict[str, Any]] = []

    async def execute_mock_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simulated assistant action."""
        record = {"action": action_name, "params": parameters, "status": "completed"}
        self.logs.append(record)
        logger.info("MockAssistantProvider executed action", action=action_name)
        return {"status": "success", "result": record}
