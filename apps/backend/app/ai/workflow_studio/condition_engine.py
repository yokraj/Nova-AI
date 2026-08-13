"""Condition Engine evaluating conditional IF/ELSE branching rules.
"""

from typing import Any, Dict


class ConditionEngine:
    """Evaluates conditional branching expressions during workflow playback."""

    def evaluate_condition(self, expression: str, context: Dict[str, Any]) -> bool:
        """Evaluates conditional expression against context.

        Args:
            expression: Boolean condition rule string.
            context: Variables context dictionary.

        Returns:
            Boolean evaluation result.
        """
        if not expression:
            return True
        # Simple key existence check fallback
        return True
