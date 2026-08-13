"""Task Decomposer breaking high-level multi-agent goals into dependency task graphs."""

import structlog

from app.ai.swarm.interfaces import ITaskDecomposer
from app.ai.swarm.models import AgentRole, SwarmMissionGraph, SwarmTask

logger = structlog.get_logger("task_decomposer")


class TaskDecomposer(ITaskDecomposer):
    """Decomposes complex goals into a Directed Acyclic Graph (DAG) of swarm tasks."""

    async def decompose_goal(self, goal: str) -> SwarmMissionGraph:
        """Decompose complex goal into structured task DAG."""
        logger.info("Decomposing multi-agent goal into task graph", goal=goal)

        # 1. Goal Analysis Task (Planner)
        t1 = SwarmTask(
            title="Analyze Goal & Plan Strategy",
            description="Decompose user request into execution plan",
            required_role=AgentRole.PLANNER,
        )

        # 2. Backend Code Review Task (Software Engineer)
        t2 = SwarmTask(
            title="Inspect Backend Architecture & Code",
            description="Review codebase structure, APIs, and performance bottlenecks",
            required_role=AgentRole.SOFTWARE_ENGINEER,
            dependencies=[t1.task_id],
        )

        # 3. Security Audit Task (Security Agent)
        t3 = SwarmTask(
            title="Perform Security Vulnerability Audit",
            description="Scan for security vulnerabilities and permission leaks",
            required_role=AgentRole.SECURITY,
            dependencies=[t1.task_id],
        )

        # 4. Performance Optimization Task (Software Engineer)
        t4 = SwarmTask(
            title="Optimize System Performance",
            description="Refactor slow queries and optimize async execution",
            required_role=AgentRole.SOFTWARE_ENGINEER,
            dependencies=[t2.task_id],
        )

        # 5. Documentation Generation Task (Documentation Agent / Research)
        t5 = SwarmTask(
            title="Generate API & System Documentation",
            description="Generate comprehensive markdown documentation",
            required_role=AgentRole.RESEARCH,
            dependencies=[t2.task_id, t3.task_id],
        )

        # 6. Deployment Task (Execution Agent)
        t6 = SwarmTask(
            title="Deploy Backend Release",
            description="Deploy optimized and audited backend package",
            required_role=AgentRole.EXECUTION,
            dependencies=[t4.task_id, t5.task_id],
        )

        tasks = [t1, t2, t3, t4, t5, t6]
        logger.info("Decomposed goal into tasks", total_tasks=len(tasks))
        return SwarmMissionGraph(goal=goal, tasks=tasks)
