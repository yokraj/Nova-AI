"""Optimizer optimizing scheduled execution batches parallel structures.
"""

import structlog
from app.ai.planner.models import DependencyGraph, ExecutionPlan, OptimizationResult

logger = structlog.get_logger("optimizer")

class Optimizer:
    """Consolidates sequential execution batches, maximizing parallel execution slots."""

    def optimize_plan(self, graph: DependencyGraph, plan: ExecutionPlan) -> OptimizationResult:
        """Compresses adjacent execution batches to reduce scheduling bottlenecks."""
        original_count = len(plan.batches)
        optimized_batches = []

        for batch in plan.batches:
            if not optimized_batches:
                optimized_batches.append(batch)
                continue

            previous_batch = optimized_batches[-1]
            # Simple batch merge optimization: merge if both adjacent batches are small
            if len(previous_batch.task_ids) < 3 and len(batch.task_ids) < 3:
                previous_batch.task_ids.extend(batch.task_ids)
                previous_batch.estimated_duration_seconds = max(
                    previous_batch.estimated_duration_seconds,
                    batch.estimated_duration_seconds
                )
            else:
                optimized_batches.append(batch)

        plan.batches = optimized_batches
        optimized_count = len(plan.batches)
        logger.info("Optimized scheduled execution plan", original_batches=original_count, optimized_batches=optimized_count)

        ratio = (original_count - optimized_count) / original_count if original_count > 0 else 0.0
        return OptimizationResult(
            original_batches_count=original_count,
            optimized_batches_count=optimized_count,
            parallelism_ratio=ratio
        )
