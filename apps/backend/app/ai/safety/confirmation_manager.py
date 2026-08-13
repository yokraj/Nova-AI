"""Confirmation Manager formatting voice confirmation prompts based on risk classification.
"""

from typing import Dict, Any
from app.ai.safety.models import RiskLevel

class ConfirmationManager:
    """Compiles conversational confirmation prompts readable by TTS voice systems."""

    def format_prompt(self, action: str, parameters: Dict[str, Any], risk_level: RiskLevel) -> str:
        """Constructs risk-aware conversational prompts."""
        if risk_level == RiskLevel.CRITICAL:
            cost = parameters.get("cost_value", "INR 1,250")
            item = parameters.get("item_name", "Vande Bharat train ticket")
            return f"This action will purchase a {item} costing {cost}. Do you approve?"

        if risk_level == RiskLevel.HIGH:
            count = parameters.get("count_value", "1,240")
            asset = parameters.get("asset_name", "files")
            return f"This will permanently delete {count} {asset}. Continue?"

        return f"Do you approve executing the action: {action}? Proceed?"
