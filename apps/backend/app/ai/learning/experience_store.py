"""In-memory Experience Store with optional overflow to LocalMemoryEngine."""

from typing import Dict, List, Optional
import structlog

from app.ai.learning.configuration import LearningConfiguration
from app.ai.learning.exceptions import ExperienceNotFoundError
from app.ai.learning.models import Experience, ExperienceOutcome

logger = structlog.get_logger("experience_store")


class ExperienceStore:
    """Thread-safe in-memory experience record store with bounded capacity.

    When the store exceeds ``max_experiences`` the oldest record is evicted
    (FIFO), ensuring bounded memory consumption without external services.
    """

    def __init__(self, config: Optional[LearningConfiguration] = None) -> None:
        self.config = config or LearningConfiguration()
        self._store: Dict[str, Experience] = {}
        self._order: List[str] = []  # Insertion order for FIFO eviction

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save_experience(self, experience: Experience) -> None:
        """Persist an experience record, evicting the oldest if capacity is exceeded."""
        if experience.experience_id in self._store:
            # Update existing record in-place
            self._store[experience.experience_id] = experience
            return

        if len(self._store) >= self.config.max_experiences:
            oldest_id = self._order.pop(0)
            self._store.pop(oldest_id, None)
            logger.debug("Evicted oldest experience", evicted_id=oldest_id)

        self._store[experience.experience_id] = experience
        self._order.append(experience.experience_id)
        logger.debug("Saved experience", experience_id=experience.experience_id)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_experience(self, experience_id: str) -> Experience:
        """Retrieve a single experience by ID.

        Raises:
            ExperienceNotFoundError: When the ID is not in the store.
        """
        exp = self._store.get(experience_id)
        if exp is None:
            raise ExperienceNotFoundError(
                f"Experience '{experience_id}' not found in store."
            )
        return exp

    def list_experiences(self) -> List[Experience]:
        """Return all stored experiences in insertion order."""
        return [self._store[eid] for eid in self._order if eid in self._store]

    def experiences_by_outcome(self, outcome: ExperienceOutcome) -> List[Experience]:
        """Filter experiences by final execution outcome."""
        return [e for e in self.list_experiences() if e.outcome == outcome]

    def experiences_for_goal_keywords(self, keywords: List[str]) -> List[Experience]:
        """Return experiences whose goal text contains at least one keyword."""
        result: List[Experience] = []
        for exp in self.list_experiences():
            goal_lower = exp.goal.lower()
            if any(kw.lower() in goal_lower for kw in keywords):
                result.append(exp)
        return result

    def recent(self, limit: int = 20) -> List[Experience]:
        """Return the most recently added experiences."""
        all_exp = self.list_experiences()
        return all_exp[-limit:] if len(all_exp) > limit else all_exp

    # ------------------------------------------------------------------
    # Aggregates
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return total number of stored experiences."""
        return len(self._store)

    def success_rate(self) -> float:
        """Compute overall success rate across all experiences."""
        total = self.count()
        if total == 0:
            return 0.0
        successful = sum(
            1
            for e in self._store.values()
            if e.outcome == ExperienceOutcome.COMPLETED
        )
        return round(successful / total, 4)

    def clear(self) -> None:
        """Remove all stored experiences (used in tests only)."""
        self._store.clear()
        self._order.clear()
