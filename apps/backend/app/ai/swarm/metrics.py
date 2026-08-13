"""Swarm Metrics Tracker recording telemetry metrics."""

import structlog

from app.ai.swarm.models import SwarmMetrics

logger = structlog.get_logger("swarm_metrics")


class SwarmMetricsTracker:
    """Tracks telemetry metrics for Swarm Intelligence Engine."""

    def __init__(self) -> None:
        self._swarms_created = 0
        self._tasks_decomposed = 0
        self._tasks_executed = 0
        self._consensus_votes = 0
        self._conflicts_resolved = 0
        self._leader_elections = 0

    def record_swarm_created(self) -> None:
        self._swarms_created += 1

    def record_tasks_decomposed(self, count: int = 1) -> None:
        self._tasks_decomposed += count

    def record_task_executed(self) -> None:
        self._tasks_executed += 1

    def record_consensus_vote(self) -> None:
        self._consensus_votes += 1

    def record_conflict_resolved(self) -> None:
        self._conflicts_resolved += 1

    def record_leader_election(self) -> None:
        self._leader_elections += 1

    def get_metrics(self) -> SwarmMetrics:
        """Get metrics snapshot."""
        return SwarmMetrics(
            swarms_created=self._swarms_created,
            tasks_decomposed=self._tasks_decomposed,
            tasks_executed=self._tasks_executed,
            consensus_votes_held=self._consensus_votes,
            conflicts_resolved=self._conflicts_resolved,
            leader_elections_held=self._leader_elections,
        )
