"""Safety Confirmation Hold Engine for sensitive operating system operations.
"""

from typing import Dict
from app.ai.os_runtime.interfaces import IConfirmationEngine
from app.ai.os_runtime.models import ConfirmationHold


class ConfirmationEngine(IConfirmationEngine):
    """Holds sensitive operations (file deletion, registry edits, admin elevation, payments, shutdowns) for user verification."""

    def __init__(self) -> None:
        self._holds: Dict[str, ConfirmationHold] = {}

    async def request_confirmation(self, action_type: str, description: str) -> ConfirmationHold:
        """Places a confirmation hold on sensitive operation."""
        hold = ConfirmationHold(
            action_type=action_type,
            description=description,
            risk_level="HIGH" if "delete" in action_type or "admin" in action_type else "MEDIUM",
            confirmed=False,
        )
        self._holds[hold.hold_id] = hold
        return hold

    async def approve_confirmation(self, hold_id: str) -> bool:
        """Approves pending confirmation hold."""
        if hold_id in self._holds:
            self._holds[hold_id].confirmed = True
            return True
        return False
