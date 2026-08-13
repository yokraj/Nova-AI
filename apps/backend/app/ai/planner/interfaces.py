"""Abstract interface contracts for Intelligent Planner systems.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from app.ai.planner.models import Goal, TaskTree, DependencyGraph, ExecutionPlan, PlanningRequest, PlanningResponse

class IGoalAnalyzer(ABC):
    """Interface for parsing goal domains and deliverables."""
    
    @abstractmethod
    async def analyze_goal(self, goal: Goal) -> Dict[str, Any]:
        pass

class IDecompositionEngine(ABC):
    """Interface for recursively building TaskTree hierarchies."""
    
    @abstractmethod
    async def decompose(self, goal: Goal) -> TaskTree:
        pass

class IDAGBuilder(ABC):
    """Interface for translating TaskTrees into DependencyGraphs."""
    
    @abstractmethod
    def build_dag(self, task_tree: TaskTree) -> DependencyGraph:
        pass

class ILocalPlannerEngine(ABC):
    """Interface for orchestrating the complete planning request pipelines."""
    
    @abstractmethod
    async def plan(self, request: PlanningRequest) -> PlanningResponse:
        pass
