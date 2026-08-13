"""Feedback Loop tracks success scores and logs learning insights.
"""

from typing import List
from app.agents.software_engineer.autonomous.models import Feedback, ImprovementSuggestion

class FeedbackLoop:
    """Consolidates execution feedback metrics."""

    def analyze_feedback(self, feedback: Feedback) -> List[ImprovementSuggestion]:
        """Examines performance scores to return improvement recommendations."""
        suggestions = []
        if not feedback.success:
            suggestions.append(ImprovementSuggestion(
                category="Execution Failure",
                issue_detected="Workflow task failed compilation or verification check.",
                recommendation="Inject dependency mock layers or check target file permissions prior to execution."
            ))
        if feedback.performance_score < 80.0:
            suggestions.append(ImprovementSuggestion(
                category="Latency Optimization",
                issue_detected="Task execution elapsed time exceeds standard threshold limits.",
                recommendation="Configure sub-engine cache parameters or optimize directory scanning recursion bounds."
            ))
        return suggestions
