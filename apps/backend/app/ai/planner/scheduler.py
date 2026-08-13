"""Scheduler grouping topological sorted graph tasks into execution batches.
"""

import structlog
from typing import Set, List
from app.ai.planner.models import DependencyGraph, ExecutionPlan, ExecutionBatch
from app.ai.planner.dependency_graph import DependencyGraphManager
from app.ai.planner.utils import generate_uuid

logger = structlog.get_logger("scheduler")

class Scheduler:
    """Constructs schedules without executing tasks, complying with dependency locks."""

    def generate_plan(self, graph: DependencyGraph) -> ExecutionPlan:
        """Translates DAG topological sorting lists into execution batches."""
        manager = DependencyGraphManager(graph)
        topological_order = manager.get_topological_sort()

        batches: List[ExecutionBatch] = []
        completed_task_ids: Set[str] = set()
        pending_task_ids = list(topological_order)
        batch_index = 1

        while pending_task_ids:
            ready_task_ids = []

            for task_id in list(pending_task_ids):
                task = graph.nodes.get(task_id)
                if not task:
                    continue

                # Ready if all prereq dependencies are already scheduled
                dependencies_satisfied = all(
                    prereq_id in completed_task_ids
                    for prereq_id in task.dependencies
                    if prereq_id in graph.nodes
                )
                if dependencies_satisfied:
                    ready_task_ids.append(task_id)

            # Prevent infinite loops in unexpected structural states
            if not ready_task_ids and pending_task_ids:
                ready_task_ids.append(pending_task_ids[0])

            # Dequeue resolved tasks
            for task_id in ready_task_ids:
                pending_task_ids.remove(task_id)
                completed_task_ids.add(task_id)

            batches.append(ExecutionBatch(
                batch_id=f"batch_{batch_index}",
                task_ids=ready_task_ids,
                estimated_duration_seconds=15.0 * len(ready_task_ids)
            ))
            batch_index += 1

        total_duration = sum(batch.estimated_duration_seconds for batch in batches)
        logger.info("Generated scheduling execution plan", batches_count=len(batches), total_duration_seconds=total_duration)

        return ExecutionPlan(
            plan_id=generate_uuid(),
            batches=batches,
            recovery_plans={},
            total_estimated_seconds=total_duration
        )
