"""Pattern Detector — identifies recurring behavioural patterns across experiences."""

import structlog
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from app.ai.learning.configuration import LearningConfiguration
from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.models import Experience, ExperienceOutcome, Pattern

logger = structlog.get_logger("pattern_detector")


class PatternDetector:
    """Scans the experience store to surface statistically significant patterns.

    Detects:
    - Frequently successful workflow types (by goal keyword clusters)
    - Common failure causes (by keyword + failure outcome)
    - Efficient agent combinations (by agents_used groupings)
    - Repeated user preferences (high approval + satisfaction)
    - Performance bottlenecks (high duration + low satisfaction)
    """

    def __init__(
        self,
        store: Optional[ExperienceStore] = None,
        config: Optional[LearningConfiguration] = None,
    ) -> None:
        self.store = store or ExperienceStore()
        self.config = config or LearningConfiguration()
        self._patterns: Dict[str, Pattern] = {}

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def detect_all(self) -> List[Pattern]:
        """Run all detection routines and return the consolidated pattern list."""
        experiences = self.store.list_experiences()
        if not experiences:
            return []

        self._detect_success_patterns(experiences)
        self._detect_failure_patterns(experiences)
        self._detect_agent_patterns(experiences)
        self._detect_preference_patterns(experiences)

        return self.list_patterns()

    def list_patterns(self) -> List[Pattern]:
        """Return all detected patterns sorted by success_rate descending."""
        return sorted(
            self._patterns.values(),
            key=lambda p: (p.success_rate, p.occurrences),
            reverse=True,
        )

    def patterns_for_goal(self, goal: str) -> List[Pattern]:
        """Return patterns whose keywords overlap with the given goal."""
        goal_words = set(goal.lower().split())
        result: List[Pattern] = []
        for pattern in self._patterns.values():
            overlap = goal_words & {kw.lower() for kw in pattern.domain_keywords}
            if overlap:
                result.append(pattern)
        return sorted(result, key=lambda p: p.success_rate, reverse=True)

    def count_pattern_matches(self) -> int:
        """Return total number of detected patterns with enough occurrences."""
        return len(
            [
                p
                for p in self._patterns.values()
                if p.occurrences >= self.config.pattern_min_occurrences
            ]
        )

    # ------------------------------------------------------------------
    # Detection Routines
    # ------------------------------------------------------------------

    def _detect_success_patterns(self, experiences: List[Experience]) -> None:
        """Cluster successful experiences by shared goal keywords."""
        buckets: Dict[str, List[Experience]] = defaultdict(list)

        for exp in experiences:
            if exp.outcome != ExperienceOutcome.COMPLETED:
                continue
            keyword = self._dominant_keyword(exp.goal)
            buckets[keyword].append(exp)

        for keyword, exps in buckets.items():
            if len(exps) < self.config.pattern_min_occurrences:
                continue
            pattern_id = f"ptn_success_{keyword}"
            rate = self._compute_success_rate(exps, keyword, experiences)
            agent_ids = list(
                {agent for e in exps for agent in e.agents_used}
            )

            pattern = self._patterns.get(pattern_id) or Pattern(
                pattern_id=pattern_id,
                name=f"Successful {keyword.title()} Workflow",
                description=(
                    f"Recurring successful pattern for '{keyword}' goals "
                    f"observed {len(exps)} times."
                ),
                domain_keywords=[keyword],
            )
            pattern.occurrences = len(exps)
            pattern.success_rate = rate
            pattern.agent_ids = agent_ids
            self._patterns[pattern_id] = pattern
            logger.debug("Success pattern updated", pattern_id=pattern_id, occurrences=len(exps))

    def _detect_failure_patterns(self, experiences: List[Experience]) -> None:
        """Cluster failure experiences to identify common failure causes."""
        buckets: Dict[str, List[Experience]] = defaultdict(list)

        for exp in experiences:
            if exp.outcome != ExperienceOutcome.FAILED:
                continue
            keyword = self._dominant_keyword(exp.goal)
            buckets[keyword].append(exp)

        for keyword, exps in buckets.items():
            if len(exps) < self.config.pattern_min_occurrences:
                continue
            pattern_id = f"ptn_failure_{keyword}"
            pattern = self._patterns.get(pattern_id) or Pattern(
                pattern_id=pattern_id,
                name=f"Recurring Failure in {keyword.title()} Tasks",
                description=(
                    f"Repeated failure pattern for '{keyword}' goals "
                    f"observed {len(exps)} times."
                ),
                domain_keywords=[keyword],
            )
            pattern.occurrences = len(exps)
            pattern.success_rate = 0.0
            self._patterns[pattern_id] = pattern

    def _detect_agent_patterns(self, experiences: List[Experience]) -> None:
        """Identify efficient agent combinations from successful experiences."""
        combo_buckets: Dict[Tuple, List[Experience]] = defaultdict(list)

        for exp in experiences:
            if exp.outcome != ExperienceOutcome.COMPLETED:
                continue
            combo_key = tuple(sorted(exp.agents_used))
            if len(combo_key) >= 2:
                combo_buckets[combo_key].append(exp)

        for combo, exps in combo_buckets.items():
            if len(exps) < self.config.pattern_min_occurrences:
                continue
            combo_str = "_".join(combo[:3])  # limit key length
            pattern_id = f"ptn_agents_{combo_str}"
            pattern = self._patterns.get(pattern_id) or Pattern(
                pattern_id=pattern_id,
                name=f"Efficient Agent Combo: {', '.join(combo[:3])}",
                description=(
                    f"Agent combination {list(combo)} achieved high success "
                    f"across {len(exps)} missions."
                ),
                domain_keywords=list(combo),
            )
            pattern.occurrences = len(exps)
            pattern.success_rate = 1.0
            pattern.agent_ids = list(combo)
            self._patterns[pattern_id] = pattern

    def _detect_preference_patterns(self, experiences: List[Experience]) -> None:
        """Surface high-satisfaction, high-approval experiences as user preferences."""
        preferred = [
            e
            for e in experiences
            if e.user_satisfaction >= 0.8 and e.approval_count == 0
        ]
        if len(preferred) >= self.config.pattern_min_occurrences:
            pattern_id = "ptn_user_preference_autonomous"
            pattern = self._patterns.get(pattern_id) or Pattern(
                pattern_id=pattern_id,
                name="Preferred Autonomous Execution Style",
                description=(
                    "User consistently prefers low-interruption, high-satisfaction "
                    "autonomous executions."
                ),
                domain_keywords=["autonomous", "low-interruption"],
            )
            pattern.occurrences = len(preferred)
            pattern.success_rate = sum(
                e.user_satisfaction for e in preferred
            ) / len(preferred)
            self._patterns[pattern_id] = pattern

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _dominant_keyword(goal: str) -> str:
        """Extract the first meaningful keyword from a goal string."""
        stop_words = {
            "a", "an", "the", "and", "or", "to", "of", "in", "for", "with",
            "build", "create", "make", "develop", "implement", "design",
        }
        words = [w.lower().strip(".,;:!?") for w in goal.split()]
        meaningful = [w for w in words if w and w not in stop_words and len(w) > 2]
        return meaningful[0] if meaningful else "generic"

    @staticmethod
    def _compute_success_rate(
        successes: List[Experience],
        keyword: str,
        all_experiences: List[Experience],
    ) -> float:
        """Compute success rate for a keyword cluster."""
        total_for_keyword = sum(
            1
            for e in all_experiences
            if keyword in e.goal.lower()
        )
        if total_for_keyword == 0:
            return 0.0
        return round(len(successes) / total_for_keyword, 4)
