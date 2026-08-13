"""Mock Ambient Provider simulating ambient events deterministically."""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger("ambient_mock_provider")


class MockAmbientProvider:
    """Deterministic offline provider for ambient intelligence testing."""

    def __init__(self) -> None:
        self.logs: List[Dict[str, Any]] = []

    async def execute_mock_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simulated ambient action."""
        record = {"action": action_name, "params": parameters, "status": "completed"}
        self.logs.append(record)
        logger.info("MockAmbientProvider executed action", action=action_name)
        return {"status": "success", "result": record}
