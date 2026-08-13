"""Decomposition Engine dividing goals recursively into subtasks hierarchies.
"""

import structlog
from typing import Dict, Any, List
from app.ai.planner.models import Goal, TaskTree, TaskNode, Task, CapabilityRequirement
from app.ai.planner.utils import generate_uuid

logger = structlog.get_logger("decomposition_engine")

class DecompositionEngine:
    """Decomposes goals recursively using domain-specific templates."""

    async def decompose(self, goal: Goal, analysis: Dict[str, Any]) -> TaskTree:
        """Splits main goal into structured task nodes matching template patterns."""
        domain = analysis.get("domain", "generic")
        logger.info("Initializing task decomposition", goal_id=goal.goal_id, domain=domain)

        root_task = Task(
            task_id=generate_uuid(),
            title=f"Root: {goal.description[:50]}",
            description=goal.description,
            domain=domain,
            priority="Critical"
        )
        root_node = TaskNode(task=root_task)

        # Decompose depending on template
        if domain == "enterprise_software":
            self._decompose_enterprise_software(root_node)
        elif domain == "scientific_research":
            self._decompose_scientific_research(root_node)
        else:
            self._decompose_generic(root_node)

        # Count total nodes
        total_nodes = self._count_nodes(root_node)
        logger.info("Decomposed goal into task tree", total_nodes=total_nodes)

        return TaskTree(root_node=root_node, total_nodes=total_nodes)

    def _decompose_enterprise_software(self, root: TaskNode) -> None:
        parent_id = root.task.task_id

        # Phase 1: Research
        research = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Research & Requirement Gathering",
            description="Analyze ERP/CRM industry specs, user flows, and core models definitions.",
            domain="research",
            priority="High",
            required_capabilities=[CapabilityRequirement(capability_name="planning")]
        )
        root.children.append(TaskNode(task=research))

        # Phase 2: Architecture
        architecture = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Architecture & System Design",
            description="Draft database schemas and interface contracts.",
            domain="architecture",
            priority="Critical",
            required_capabilities=[CapabilityRequirement(capability_name="planning")]
        )
        root.children.append(TaskNode(task=architecture))

        # Phase 3: Backend
        backend_root = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Backend Implementation",
            description="Implement API controllers, models, and authentication services.",
            domain="backend",
            priority="High"
        )
        backend_node = TaskNode(task=backend_root)
        root.children.append(backend_node)

        # Sub-tasks under backend
        database = Task(
            task_id=generate_uuid(),
            parent_id=backend_root.task_id,
            title="Database Setup",
            description="Initialize migrations and database tables.",
            domain="database",
            priority="High",
            required_capabilities=[CapabilityRequirement(capability_name="migration")]
        )
        backend_node.children.append(TaskNode(task=database))

        auth = Task(
            task_id=generate_uuid(),
            parent_id=backend_root.task_id,
            title="Authentication APIs",
            description="Build signup, login, and token generation paths.",
            domain="authentication",
            priority="High",
            required_capabilities=[CapabilityRequirement(capability_name="security")]
        )
        backend_node.children.append(TaskNode(task=auth))

        apis = Task(
            task_id=generate_uuid(),
            parent_id=backend_root.task_id,
            title="API Controllers",
            description="Implement core resource CRUD controllers.",
            domain="backend_development",
            priority="High",
            required_capabilities=[CapabilityRequirement(capability_name="api")]
        )
        backend_node.children.append(TaskNode(task=apis))

        # Phase 4: Frontend
        frontend = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Frontend UI Development",
            description="Create clean, beautiful, responsive user layout dashboard.",
            domain="frontend",
            priority="Medium",
            required_capabilities=[CapabilityRequirement(capability_name="frontend")]
        )
        root.children.append(TaskNode(task=frontend))

        # Phase 5: Testing & Verification
        testing = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Testing & Code Validation",
            description="Write pytest suites verifying backend routes.",
            domain="testing",
            priority="Medium",
            required_capabilities=[CapabilityRequirement(capability_name="testing")]
        )
        root.children.append(TaskNode(task=testing))

    def _decompose_scientific_research(self, root: TaskNode) -> None:
        parent_id = root.task.task_id

        lit_review = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Literature Review",
            description="Search EuropePMC/ArXiv for similar studies.",
            domain="research",
            priority="High",
            required_capabilities=[CapabilityRequirement(capability_name="literature_search")]
        )
        root.children.append(TaskNode(task=lit_review))

        analysis = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Data Extraction & Analysis",
            description="Compile results tables and compare constraints.",
            domain="analysis",
            priority="High",
            required_capabilities=[CapabilityRequirement(capability_name="document_analysis")]
        )
        root.children.append(TaskNode(task=analysis))

    def _decompose_generic(self, root: TaskNode) -> None:
        parent_id = root.task.task_id

        task1 = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Planning & Initial Steps",
            description="Analyze objective and layout execution steps.",
            domain="generic",
            priority="Medium",
            required_capabilities=[CapabilityRequirement(capability_name="planning")]
        )
        root.children.append(TaskNode(task=task1))

        task2 = Task(
            task_id=generate_uuid(),
            parent_id=parent_id,
            title="Finalizing Deliverables",
            description="Compile outputs and generate summary.",
            domain="generic",
            priority="Medium",
            required_capabilities=[CapabilityRequirement(capability_name="planning")]
        )
        root.children.append(TaskNode(task=task2))

    def _count_nodes(self, node: TaskNode) -> int:
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count
