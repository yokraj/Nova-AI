"""Confirmation Manager formulating clear pre-execution user confirmation summaries."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("confirmation_manager")


class ConfirmationManager:
    """Formulates human-readable summary before executing major actions or transactions."""

    async def build_confirmation_summary(self, action_name: str, parameters: Dict[str, Any]) -> str:
        """Construct confirmation text for voice or UI modal."""
        if "train" in action_name or "booking" in action_name:
            source = parameters.get("source", "Bangalore")
            dest = parameters.get("destination", "Chennai")
            return f"Confirm train booking from {source} to {dest} for tomorrow (320.0 INR)?"
        elif "passport" in action_name:
            return "Confirm submission of passport renewal application to Passport Seva Kendra?"
        return f"Confirm execution of '{action_name}' with parameters {parameters}?"
