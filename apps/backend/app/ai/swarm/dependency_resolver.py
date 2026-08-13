"""Dependency Resolver ordering task execution tiers for parallel execution."""

from typing import List
import structlog

from app.ai.swarm.models import SwarmMissionGraph, SwarmTask

logger = structlog.get_logger("dependency_resolver")


class DependencyResolver:
    """Resolves task graph dependencies into parallel execution waves."""

    def resolve_execution_waves(self, graph: SwarmMissionGraph) -> List[List[SwarmTask]]:
        """Group tasks into parallel execution waves."""
        remaining = list(graph.tasks)
        completed_ids = set()
        waves: List[List[SwarmTask]] = []

        while remaining:
            wave = [t for t in remaining if all(dep in completed_ids for dep in t.dependencies)]
            if not wave:
                # Fallback to prevent deadlocks
                wave = [remaining.pop(0)]
            else:
                for t in wave:
                    remaining.remove(t)
            for t in wave:
                completed_ids.add(t.task_id)
            waves.append(wave)

        logger.info("Resolved task graph into execution waves", wave_count=len(waves))
        return waves
