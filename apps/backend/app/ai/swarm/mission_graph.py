"""Mission Graph representing Directed Acyclic Graph (DAG) of swarm tasks."""

from typing import List
import structlog

from app.ai.swarm.models import SwarmMissionGraph, SwarmTask

logger = structlog.get_logger("mission_graph")


class MissionGraph:
    """DAG wrapper for task dependencies and execution order."""

    def __init__(self, graph: SwarmMissionGraph) -> None:
        self.graph = graph

    def get_ready_tasks(self) -> List[SwarmTask]:
        """Find pending tasks whose dependencies are completed."""
        completed_ids = {t.task_id for t in self.graph.tasks if t.state.value == "completed"}
        ready: List[SwarmTask] = []
        for t in self.graph.tasks:
            if t.state.value == "pending":
                if all(dep in completed_ids for dep in t.dependencies):
                    ready.append(t)
        return ready
