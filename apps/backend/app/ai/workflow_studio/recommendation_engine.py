"""Recommendation Engine suggesting workflow templates and optimizations.
"""

from typing import Any, Dict, List


class RecommendationEngine:
    """Generates recommendations for workflow creation, step optimizations, and triggers."""

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Returns list of workflow automation suggestions."""
        return [
            {
                "title": "Automate E-Commerce Invoice Processing",
                "description": "Nova observed 4 manual invoice downloads. Create 1-click voice workflow?",
                "suggested_trigger": "Hey Nova, process invoices",
            },
            {
                "title": "Schedule Monthly GST Filing",
                "description": "Set up monthly automated GST portal login workflow.",
                "suggested_trigger": "Schedule: 1st of every month",
            },
        ]
