"""Research Planner generating structured plans, sub-questions, and search strategies.
"""

from typing import Any, List
from app.ai.research.interfaces import IResearchPlanner
from app.ai.research.models import (
    ResearchPlan,
    SearchStrategy,
    SourceType,
    SubQuestion,
)


class ResearchPlanner(IResearchPlanner):
    """Decomposes research inquiries into sub-questions, roadmaps, and search strategies."""

    async def create_plan(self, topic: str, **kwargs: Any) -> ResearchPlan:
        """Generates research roadmap and decomposed sub-questions.

        Args:
            topic: Raw research prompt string.
            **kwargs: Additional parameters (e.g., mode='deep').

        Returns:
            Structured ResearchPlan instance.
        """
        mode = kwargs.get("mode", "fast")
        is_deep = mode == "deep" or "deep" in topic.lower() or "architecture" in topic.lower()

        sub_q1 = SubQuestion(
            query=f"Overview and core concepts of {topic}",
            category="overview",
            required_sources=[SourceType.LOCAL_FILE, SourceType.WEB_PAGE],
            estimated_time_sec=45.0,
        )

        sub_q2 = SubQuestion(
            query=f"Technical architecture and implementation details for {topic}",
            category="architecture",
            required_sources=[SourceType.REPOSITORY, SourceType.DOCUMENT],
            estimated_time_sec=60.0,
        )

        sub_q3 = SubQuestion(
            query=f"Best practices, benchmarks, and comparisons for {topic}",
            category="comparison",
            required_sources=[SourceType.WEB_PAGE, SourceType.API],
            estimated_time_sec=60.0,
        )

        sub_questions: List[SubQuestion] = [sub_q1, sub_q2, sub_q3]

        if is_deep:
            sub_q4 = SubQuestion(
                query=f"Common errors, security implications, and edge cases for {topic}",
                category="deep_dive",
                required_sources=[SourceType.PDF, SourceType.OCR_IMAGE],
                estimated_time_sec=120.0,
            )
            sub_questions.append(sub_q4)

        strategy = SearchStrategy(
            primary_sources=[SourceType.LOCAL_FILE, SourceType.REPOSITORY, SourceType.WEB_PAGE],
            use_browser=is_deep,
            max_depth=3 if is_deep else 1,
            keywords=[topic, "architecture", "best practices", "API reference"],
        )

        total_time = sum(sq.estimated_time_sec for sq in sub_questions)

        return ResearchPlan(
            topic=topic,
            goals=[f"Understand {topic}", f"Analyze architecture for {topic}", f"Identify best practices"],
            sub_questions=sub_questions,
            strategy=strategy,
            estimated_time_sec=total_time,
            complexity="high" if is_deep else "medium",
        )
