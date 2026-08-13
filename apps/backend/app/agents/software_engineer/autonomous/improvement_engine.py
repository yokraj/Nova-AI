"""Improvement Engine compiles recommendations to optimize future execution.
"""

from typing import List
from app.agents.software_engineer.autonomous.interfaces import IImprovementEngine
from app.agents.software_engineer.autonomous.models import Feedback, ImprovementSuggestion
from app.agents.software_engineer.autonomous.feedback_loop import FeedbackLoop

class LocalImprovementEngine(IImprovementEngine):
    """Aggregates execution metrics to provide improvement suggestions."""

    def __init__(self) -> None:
        self.loop = FeedbackLoop()

    def analyze_feedback(self, feedback: Feedback) -> List[ImprovementSuggestion]:
        """Runs the loop diagnostics to parse suggestions."""
        return self.loop.analyze_feedback(feedback)
