"""Task Planner Module.

Implements TaskPlanner providing goal analysis, complexity estimation, tool/agent selection,
execution time estimation, dependency identification, and subtask decomposition.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.intelligence.tool_router import ToolRouter
from app.intelligence.agent_router import AgentRouter
from app.intelligence.task_decomposer import TaskDecomposer

logger = structlog.get_logger(__name__)


class TaskPlanner:
    """Enterprise Master Task Planning & Dependency Orchestrator."""

    def __init__(
        self,
        tool_router: Optional[ToolRouter] = None,
        agent_router: Optional[AgentRouter] = None,
        task_decomposer: Optional[TaskDecomposer] = None,
    ) -> None:
        self.tool_router = tool_router or ToolRouter()
        self.agent_router = agent_router or AgentRouter()
        self.task_decomposer = task_decomposer or TaskDecomposer()
        logger.info("task_planner_initialized")

    def analyze_goal(self, goal: str) -> Dict[str, Any]:
        """Analyzes high-level goal structure and identifies key domains."""
        complexity = self.estimate_complexity(goal)
        return {
            "goal": goal,
            "complexity": complexity,
            "requires_decomposition": complexity > 3,
        }

    def estimate_complexity(self, goal: str) -> int:
        """Estimates complexity score on a scale of 1 (trivial) to 10 (highly complex)."""
        goal_length = len(goal.split())
        if goal_length < 5:
            return 1
        elif goal_length < 15:
            return 3
        elif goal_length < 30:
            return 6
        else:
            return 9

    def select_tools(self, goal: str) -> List[Dict[str, Any]]:
        """Determines necessary tools for executing the goal."""
        return self.tool_router.evaluate_tool_needs(goal)

    def select_agents(self, goal: str) -> Dict[str, Any]:
        """Selects primary workforce agent for the goal."""
        return self.agent_router.select_agent(goal)

    def estimate_execution_time(self, complexity: int, subtask_count: int) -> float:
        """Estimates total execution time in seconds based on complexity and subtask count."""
        base_seconds = 2.0
        return round(base_seconds + (complexity * 1.5) + (subtask_count * 2.5), 2)

    def identify_dependencies(self, subtasks: List[Dict[str, Any]]) -> Dict[int, List[int]]:
        """Extracts dependency mappings from a list of subtasks."""
        return {st["id"]: st.get("dependencies", []) for st in subtasks}

    def break_into_subtasks(self, goal: str) -> List[Dict[str, Any]]:
        """Decomposes goal into ordered list of subtasks."""
        decomposition = self.task_decomposer.decompose(goal)
        return decomposition.get("subtasks", [])

    def create_plan(self, goal: str) -> Dict[str, Any]:
        """Generates a complete, production-ready execution plan for target goal."""
        analysis = self.analyze_goal(goal)
        subtasks = self.break_into_subtasks(goal)
        dependencies = self.identify_dependencies(subtasks)
        tools = self.select_tools(goal)
        primary_agent = self.select_agents(goal)
        estimated_time = self.estimate_execution_time(analysis["complexity"], len(subtasks))

        plan = {
            "goal": goal,
            "complexity_score": analysis["complexity"],
            "subtask_count": len(subtasks),
            "estimated_time_seconds": estimated_time,
            "primary_agent": primary_agent,
            "required_tools": tools,
            "dependencies": dependencies,
            "subtasks": subtasks,
        }

        logger.info("plan_created", goal_snippet=goal[:40], subtasks=len(subtasks))
        return plan
