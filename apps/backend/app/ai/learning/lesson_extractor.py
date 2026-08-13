"""Lesson Extractor — generates structured lessons from Experience records."""

import structlog
from typing import List, Optional

from app.ai.learning.exceptions import LessonExtractionError
from app.ai.learning.models import (
    Experience,
    ExperienceOutcome,
    ExperienceType,
    Lesson,
    LessonCategory,
)

logger = structlog.get_logger("lesson_extractor")


class LessonExtractor:
    """Derives structured, human-readable lessons from an Experience record.

    For every completed experience it generates *success lessons* highlighting
    what worked well.  For every failed experience it generates *failure lessons*
    explaining what went wrong.  For recovered experiences it generates both.
    Optimisation lessons are derived when duration is unusually high.
    """

    # Threshold above which duration is flagged as a potential bottleneck
    SLOW_EXECUTION_THRESHOLD_SECONDS: float = 120.0

    def extract(self, experience: Experience) -> List[Lesson]:
        """Generate all applicable lessons for the given experience.

        Args:
            experience: The experience record to analyse.

        Returns:
            A list of one or more Lesson objects.

        Raises:
            LessonExtractionError: When extraction fails unexpectedly.
        """
        try:
            lessons: List[Lesson] = []

            if experience.outcome == ExperienceOutcome.COMPLETED:
                lessons.extend(self._success_lessons(experience))
            elif experience.outcome == ExperienceOutcome.FAILED:
                lessons.extend(self._failure_lessons(experience))
            elif experience.outcome == ExperienceOutcome.RECOVERED:
                lessons.extend(self._success_lessons(experience))
                lessons.extend(self._recovery_lessons(experience))

            # Optimisation lessons apply regardless of outcome
            opt = self._optimisation_lesson(experience)
            if opt:
                lessons.append(opt)

            logger.debug(
                "Extracted lessons",
                experience_id=experience.experience_id,
                count=len(lessons),
            )
            return lessons

        except Exception as err:
            raise LessonExtractionError(
                f"Failed to extract lessons for {experience.experience_id}: {err}"
            ) from err

    def extract_many(self, experiences: List[Experience]) -> List[Lesson]:
        """Extract lessons from a batch of experiences."""
        all_lessons: List[Lesson] = []
        for exp in experiences:
            try:
                all_lessons.extend(self.extract(exp))
            except LessonExtractionError as err:
                logger.warning("Lesson extraction failed for experience", error=str(err))
        return all_lessons

    # ------------------------------------------------------------------
    # Private lesson generators
    # ------------------------------------------------------------------

    def _success_lessons(self, experience: Experience) -> List[Lesson]:
        """Generate lessons celebrating what made the experience succeed."""
        lessons: List[Lesson] = []

        # Agent collaboration lesson
        if len(experience.agents_used) > 1:
            agent_list = ", ".join(experience.agents_used)
            lessons.append(
                Lesson(
                    experience_id=experience.experience_id,
                    content=(
                        f"✓ Parallel execution by agents [{agent_list}] "
                        f"reduced completion time for '{experience.goal}'."
                    ),
                    category=LessonCategory.SUCCESS,
                    confidence=0.85,
                )
            )

        # High satisfaction lesson
        if experience.user_satisfaction >= 0.8:
            lessons.append(
                Lesson(
                    experience_id=experience.experience_id,
                    content=(
                        f"✓ Execution strategy for '{experience.goal}' achieved "
                        f"high user satisfaction ({experience.user_satisfaction:.0%})."
                    ),
                    category=LessonCategory.SUCCESS,
                    confidence=0.90,
                )
            )

        # Zero-approval autonomous lesson
        if experience.approval_count == 0:
            lessons.append(
                Lesson(
                    experience_id=experience.experience_id,
                    content=(
                        f"✓ '{experience.goal}' completed fully autonomously "
                        f"with zero human interventions."
                    ),
                    category=LessonCategory.SUCCESS,
                    confidence=0.80,
                )
            )

        # Fallback generic success lesson when no specific signals
        if not lessons:
            lessons.append(
                Lesson(
                    experience_id=experience.experience_id,
                    content=f"✓ Mission '{experience.goal}' completed successfully.",
                    category=LessonCategory.SUCCESS,
                    confidence=0.75,
                )
            )

        return lessons

    def _failure_lessons(self, experience: Experience) -> List[Lesson]:
        """Generate lessons documenting failure causes and prevention."""
        lessons: List[Lesson] = []

        lessons.append(
            Lesson(
                experience_id=experience.experience_id,
                content=(
                    f"✗ Mission '{experience.goal}' failed. "
                    "Investigate prerequisites and agent assignments before retrying."
                ),
                category=LessonCategory.FAILURE,
                confidence=0.80,
            )
        )

        # Multi-agent failure — suggest re-evaluation
        if len(experience.agents_used) > 1:
            lessons.append(
                Lesson(
                    experience_id=experience.experience_id,
                    content=(
                        "✗ Multi-agent coordination failed. Consider reducing agent count "
                        "or adding a synchronisation checkpoint."
                    ),
                    category=LessonCategory.FAILURE,
                    confidence=0.70,
                )
            )

        return lessons

    def _recovery_lessons(self, experience: Experience) -> List[Lesson]:
        """Generate lessons from recovery attempts."""
        return [
            Lesson(
                experience_id=experience.experience_id,
                content=(
                    f"⟳ '{experience.goal}' required {experience.recovery_count} "
                    "recovery attempt(s) before completing. "
                    "Consider adding pre-flight validation to avoid recovery paths."
                ),
                category=LessonCategory.WARNING,
                confidence=0.75,
            )
        ]

    def _optimisation_lesson(self, experience: Experience) -> Optional[Lesson]:
        """Generate an optimisation lesson when execution was slow."""
        if experience.duration_seconds > self.SLOW_EXECUTION_THRESHOLD_SECONDS:
            return Lesson(
                experience_id=experience.experience_id,
                content=(
                    f"⚡ '{experience.goal}' took {experience.duration_seconds:.0f}s. "
                    "Consider parallelising independent subtasks or caching intermediate results."
                ),
                category=LessonCategory.OPTIMIZATION,
                confidence=0.72,
            )
        return None
