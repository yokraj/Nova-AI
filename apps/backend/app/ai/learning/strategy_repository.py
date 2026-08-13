"""Strategy Repository — stores, versions, ranks, and retrieves reusable strategies."""

import structlog
from datetime import datetime
from typing import Dict, List, Optional

from app.ai.learning.configuration import LearningConfiguration
from app.ai.learning.exceptions import StrategyNotFoundError
from app.ai.learning.models import Strategy

logger = structlog.get_logger("strategy_repository")


# ---------------------------------------------------------------------------
# Built-in seed strategies (one per canonical domain)
# ---------------------------------------------------------------------------

_SEED_STRATEGIES: List[Dict] = [
    {
        "name": "Structured Planning Strategy",
        "domain": "planning",
        "description": (
            "Decompose the goal into atomic tasks. Assign agents by capability. "
            "Estimate durations. Build dependency DAG. Optimise schedule. Validate plan."
        ),
        "steps": [
            "Analyse goal intent and domain",
            "Decompose into atomic subtasks",
            "Match capabilities to agents",
            "Construct dependency DAG",
            "Optimise execution order",
            "Validate and lock plan",
        ],
        "tags": ["planning", "decomposition", "dag"],
        "success_rate": 0.85,
    },
    {
        "name": "Incremental Coding Strategy",
        "domain": "coding",
        "description": (
            "Scaffold project structure first. Implement core logic. Add tests. "
            "Refactor. Document."
        ),
        "steps": [
            "Scaffold project and directory structure",
            "Implement domain models and interfaces",
            "Implement core business logic",
            "Write unit tests",
            "Refactor and optimise",
            "Write documentation",
        ],
        "tags": ["coding", "tdd", "modular"],
        "success_rate": 0.88,
    },
    {
        "name": "Root Cause Debugging Strategy",
        "domain": "debugging",
        "description": (
            "Reproduce the bug. Isolate scope. Identify root cause. "
            "Apply minimal fix. Verify regression-free."
        ),
        "steps": [
            "Reproduce the failing behaviour",
            "Isolate the affected scope",
            "Read logs and stack traces",
            "Identify root cause",
            "Apply minimal surgical fix",
            "Run regression suite",
        ],
        "tags": ["debugging", "root-cause", "regression"],
        "success_rate": 0.82,
    },
    {
        "name": "Component-First UI Design Strategy",
        "domain": "ui_design",
        "description": (
            "Define design tokens. Build atomic components. Compose into layouts. "
            "Add animations. Verify accessibility."
        ),
        "steps": [
            "Define colour, typography, and spacing tokens",
            "Build atomic UI components",
            "Compose components into page layouts",
            "Add micro-animations and transitions",
            "Verify accessibility and responsiveness",
        ],
        "tags": ["ui", "design", "components", "accessibility"],
        "success_rate": 0.80,
    },
    {
        "name": "Blue-Green Deployment Strategy",
        "domain": "deployment",
        "description": (
            "Build artefact. Run pre-flight checks. Deploy to staging. "
            "Smoke test. Promote to production. Monitor."
        ),
        "steps": [
            "Build production artefact",
            "Run pre-flight static checks",
            "Deploy to staging environment",
            "Execute smoke tests",
            "Promote to production slot",
            "Monitor error rates for 15 minutes",
        ],
        "tags": ["deployment", "blue-green", "staging"],
        "success_rate": 0.90,
    },
    {
        "name": "Pyramid Testing Strategy",
        "domain": "testing",
        "description": (
            "Write unit tests for all logic. Integration tests for service boundaries. "
            "E2E tests for critical paths."
        ),
        "steps": [
            "Write unit tests for all business logic",
            "Write integration tests for API boundaries",
            "Write E2E tests for critical user paths",
            "Measure coverage and fix gaps",
            "Add performance benchmarks",
        ],
        "tags": ["testing", "pyramid", "coverage"],
        "success_rate": 0.87,
    },
]


class StrategyRepository:
    """Versioned, ranked repository of reusable execution strategies.

    Strategies are stored per domain. When a new version of an existing
    strategy is saved, the version counter is incremented and the repository
    evicts the oldest version if ``strategy_max_versions`` is exceeded.
    """

    def __init__(
        self,
        config: Optional[LearningConfiguration] = None,
    ) -> None:
        self.config = config or LearningConfiguration()
        # domain -> List[Strategy] (ordered newest-first)
        self._store: Dict[str, List[Strategy]] = {}
        self._seed()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save_strategy(self, strategy: Strategy) -> None:
        """Persist a strategy, auto-incrementing its version."""
        domain = strategy.domain
        existing = self._store.setdefault(domain, [])

        # Find previous version by name
        prev = next((s for s in existing if s.name == strategy.name), None)
        if prev is not None:
            strategy.version = prev.version + 1
            strategy.updated_at = datetime.utcnow()
            existing.remove(prev)
        else:
            strategy.version = 1

        # Insert newest at front
        existing.insert(0, strategy)

        # Evict oldest if over max
        if len(existing) > self.config.strategy_max_versions:
            evicted = existing.pop()
            logger.debug(
                "Evicted old strategy version",
                strategy=evicted.name,
                version=evicted.version,
            )

        logger.info(
            "Saved strategy",
            strategy_id=strategy.strategy_id,
            domain=domain,
            version=strategy.version,
        )

    def update_success_rate(self, strategy_id: str, new_rate: float) -> None:
        """Update the success_rate of a strategy by its ID."""
        for strategies in self._store.values():
            for s in strategies:
                if s.strategy_id == strategy_id:
                    s.success_rate = round(new_rate, 4)
                    s.usage_count += 1
                    s.updated_at = datetime.utcnow()
                    return

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_domain(self, domain: str) -> List[Strategy]:
        """Return all strategy versions for a given domain, newest first."""
        return list(self._store.get(domain, []))

    def best_strategy(self, domain: str) -> Optional[Strategy]:
        """Return the highest success_rate strategy for a domain."""
        strategies = self.get_by_domain(domain)
        if not strategies:
            return None
        return max(strategies, key=lambda s: (s.success_rate, s.usage_count))

    def best_for_keywords(self, keywords: List[str]) -> Optional[Strategy]:
        """Return the best strategy whose tags or domain overlap with keywords."""
        candidates: List[Strategy] = []
        for domain, strategies in self._store.items():
            for s in strategies:
                all_terms = s.tags + [s.domain] + [s.name.lower()]
                if any(kw.lower() in " ".join(all_terms) for kw in keywords):
                    candidates.append(s)
        if not candidates:
            return None
        return max(candidates, key=lambda s: (s.success_rate, s.usage_count))

    def get_by_id(self, strategy_id: str) -> Optional[Strategy]:
        """Return a specific strategy by its ID."""
        for strategies in self._store.values():
            for s in strategies:
                if s.strategy_id == strategy_id:
                    return s
        return None

    def list_all(self) -> List[Strategy]:
        """Return all strategies across all domains, ranked by success_rate."""
        all_strategies = [s for strategies in self._store.values() for s in strategies]
        return sorted(all_strategies, key=lambda s: s.success_rate, reverse=True)

    def count(self) -> int:
        """Return total number of strategy records (all versions)."""
        return sum(len(v) for v in self._store.values())

    # ------------------------------------------------------------------
    # Seed
    # ------------------------------------------------------------------

    def _seed(self) -> None:
        """Populate the repository with built-in strategies for each canonical domain."""
        for data in _SEED_STRATEGIES:
            s = Strategy(
                name=data["name"],
                domain=data["domain"],
                description=data["description"],
                steps=data["steps"],
                tags=data["tags"],
                success_rate=data["success_rate"],
            )
            self._store.setdefault(s.domain, []).append(s)
        logger.debug("Strategy repository seeded", total=self.count())
