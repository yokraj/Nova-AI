"""Resource Planner schedules task assignments and agent execution capacity.
"""

from typing import List
from app.agents.software_engineer.project_manager.models import Project, ResourceAllocation, Task

class ResourcePlanner:
    """Manages agent workloads and capability balances."""

    def allocate_resources(self, project: Project, tasks: List[Task]) -> List[ResourceAllocation]:
        """Allocates tasks to software engineering agents based on capacity limits."""
        allocations = [
            ResourceAllocation(agent_id="software-engineer-agent-1", capacity_hours=40.0, assigned_tasks=[]),
            ResourceAllocation(agent_id="testing-agent-1", capacity_hours=40.0, assigned_tasks=[])
        ]

        for idx, task in enumerate(tasks):
            # Balance allocation: even tasks to software engineer, odd to testing agent
            alloc_index = idx % len(allocations)
            allocations[alloc_index].assigned_tasks.append(task.id)

        project.resource_allocations = allocations
        return allocations
