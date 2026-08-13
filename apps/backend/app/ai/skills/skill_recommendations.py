"""Skill Recommendation Engine analyzing user workflow patterns and recommending new skills.
"""

from typing import List
from app.ai.skills.models import SkillMetadata


class SkillRecommendationEngine:
    """Analyzes workspace usage and recommends relevant new skills and updates."""

    def recommend_skills(self, available_skills: List[SkillMetadata]) -> List[SkillMetadata]:
        """Generates list of top recommended skills.

        Args:
            available_skills: List of available SkillMetadata instances.

        Returns:
            Recommended list of SkillMetadata instances.
        """
        # Recommend highly rated skills first
        sorted_skills = sorted(available_skills, key=lambda s: s.rating, reverse=True)
        return sorted_skills[:3]
