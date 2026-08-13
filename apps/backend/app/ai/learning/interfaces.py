"""Abstract interface contracts for the Continuous Learning & Shared Experience Engine."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.ai.learning.models import (
    AgentExperience,
    Experience,
    LearningMetrics,
    Lesson,
    Pattern,
    Recommendation,
    Strategy,
)


class ILearningEngine(ABC):
    """Top-level interface for the Continuous Learning & Shared Experience Engine."""

    @abstractmethod
    async def learn_from_mission(
        self,
        mission_id: str,
        mission_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process a completed or failed mission and store its experience."""

    @abstractmethod
    async def recommend_strategy(self, goal: str) -> Dict[str, Any]:
        """Return the best available strategy for a given goal description."""

    @abstractmethod
    async def agent_experience(self, agent_id: str) -> Dict[str, Any]:
        """Return the accumulated experience record for a specific agent."""

    @abstractmethod
    async def best_workflow(self, task: str) -> Dict[str, Any]:
        """Return the highest-ranked reusable workflow template for a task."""

    @abstractmethod
    async def learning_metrics(self) -> Dict[str, Any]:
        """Return a snapshot of all learning KPIs."""

    @abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """Return a composite health status of all sub-systems."""


class IExperienceStore(ABC):
    """Interface for experience persistence backends."""

    @abstractmethod
    def save_experience(self, experience: Experience) -> None:
        pass

    @abstractmethod
    def get_experience(self, experience_id: str) -> Experience:
        pass

    @abstractmethod
    def list_experiences(self) -> List[Experience]:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class IStrategyRepository(ABC):
    """Interface for the strategy storage and retrieval layer."""

    @abstractmethod
    def save_strategy(self, strategy: Strategy) -> None:
        pass

    @abstractmethod
    def get_by_domain(self, domain: str) -> List[Strategy]:
        pass

    @abstractmethod
    def best_strategy(self, domain: str) -> Strategy:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class IRecommendationEngine(ABC):
    """Interface for recommendation generation."""

    @abstractmethod
    def recommend_for_goal(self, goal: str) -> List[Recommendation]:
        pass

    @abstractmethod
    def recommend_for_agent(self, agent_id: str) -> List[Recommendation]:
        pass
