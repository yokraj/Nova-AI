"""Central Continuous Learning & Shared Experience Engine."""

import structlog
from typing import Any, Dict, List, Optional

from app.ai.learning.agent_memory import AgentMemory
from app.ai.learning.collaboration_learning import CollaborationLearning
from app.ai.learning.configuration import LearningConfiguration
from app.ai.learning.experience_manager import ExperienceManager
from app.ai.learning.experience_store import ExperienceStore
from app.ai.learning.health import LearningHealthMonitor
from app.ai.learning.interfaces import ILearningEngine
from app.ai.learning.lesson_extractor import LessonExtractor
from app.ai.learning.memory import LearningMemory
from app.ai.learning.metrics import LearningMetricsTracker
from app.ai.learning.mission_feedback import MissionFeedback
from app.ai.learning.models import ExperienceOutcome
from app.ai.learning.pattern_detector import PatternDetector
from app.ai.learning.planner_feedback import PlannerFeedback
from app.ai.learning.providers.mock_provider import MockLearningProvider
from app.ai.learning.recommendation_engine import RecommendationEngine
from app.ai.learning.safety_feedback import SafetyFeedback
from app.ai.learning.strategy_repository import StrategyRepository
from app.ai.learning.workflow_feedback import WorkflowFeedback

logger = structlog.get_logger("learning_engine")


class LearningEngine(ILearningEngine):
    """The central Continuous Learning & Shared Experience Engine.

    Orchestrates the full learning lifecycle:
    1. Accepts completed or failed mission result dicts
    2. Builds and stores canonical Experience records
    3. Extracts structured lessons
    4. Detects recurring patterns
    5. Updates strategy success rates
    6. Updates per-agent knowledge records
    7. Persists summaries to the RAG memory store
    8. Exposes recommendations to Planner, Workflow, Mission, and Safety engines
    """

    def __init__(
        self,
        memory_engine: Optional[Any] = None,
        config: Optional[LearningConfiguration] = None,
    ) -> None:
        self.config = config or LearningConfiguration()

        # Storage
        self.store = ExperienceStore(config=self.config)
        self.manager = ExperienceManager(store=self.store)

        # Intelligence
        self.pattern_detector = PatternDetector(store=self.store, config=self.config)
        self.strategy_repo = StrategyRepository(config=self.config)
        self.lesson_extractor = LessonExtractor()
        self.recommender = RecommendationEngine(
            store=self.store,
            pattern_detector=self.pattern_detector,
            strategy_repo=self.strategy_repo,
            config=self.config,
        )
        self.agent_memory = AgentMemory(store=self.store, config=self.config)
        self.collaboration = CollaborationLearning(
            store=self.store,
            agent_memory=self.agent_memory,
            config=self.config,
        )

        # Feedback channels
        self.planner_feedback = PlannerFeedback(
            store=self.store,
            strategy_repo=self.strategy_repo,
            recommendation_engine=self.recommender,
        )
        self.workflow_feedback = WorkflowFeedback(
            store=self.store,
            strategy_repo=self.strategy_repo,
            recommendation_engine=self.recommender,
        )
        self.mission_feedback = MissionFeedback(store=self.store)
        self.safety_feedback = SafetyFeedback(store=self.store)

        # Observability
        self.metrics = LearningMetricsTracker()
        self.health = LearningHealthMonitor(
            experience_store=self.store,
            pattern_detector=self.pattern_detector,
            strategy_repository=self.strategy_repo,
            recommendation_engine=self.recommender,
        )

        # Persistence bridge
        self.memory = LearningMemory(memory_engine=memory_engine)

        # Offline provider
        self.mock = MockLearningProvider()

        logger.info("LearningEngine initialised", storage_path=self.config.storage_path)

    # ------------------------------------------------------------------
    # Primary API
    # ------------------------------------------------------------------

    async def learn_from_mission(
        self,
        mission_id: str,
        mission_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process a completed or failed mission and update all learning sub-systems.

        Args:
            mission_id: Unique identifier of the completed mission.
            mission_result: Dict containing status, duration_seconds, agents_used, etc.

        Returns:
            Summary dict with experience_id, lessons, patterns, recommendations.
        """
        goal = mission_result.get("goal", "Unknown mission goal")
        logger.info("Learning from mission", mission_id=mission_id, goal=goal)

        # 1. Build and persist experience
        experience = self.manager.build_experience(
            mission_id=mission_id,
            goal=goal,
            result=mission_result,
        )
        is_success = experience.outcome == ExperienceOutcome.COMPLETED
        self.metrics.record_experience(success=is_success)

        # 2. Extract lessons
        lessons = self.lesson_extractor.extract(experience)

        # 3. Detect patterns (incremental scan)
        patterns = self.pattern_detector.detect_all()
        self.metrics.set_pattern_matches(len(patterns))

        # 4. Update agent memory
        for agent_id in experience.agents_used:
            self.agent_memory.record_experience(
                agent_id=agent_id,
                experience_outcome=experience.outcome.value,
                goal=goal,
                duration=experience.duration_seconds,
            )

        # 5. Cross-agent knowledge sync
        if experience.agents_used:
            self.collaboration.sync_team_knowledge(experience.agents_used)

        # 6. Update workflow feedback stats
        self.workflow_feedback.update_from_store()

        # 7. Record mission feedback
        self.mission_feedback.record_mission(
            mission_id=mission_id,
            goal=goal,
            outcome=experience.outcome.value,
            duration_seconds=experience.duration_seconds,
            recovery_count=experience.recovery_count,
            approval_count=experience.approval_count,
            user_satisfaction=experience.user_satisfaction,
        )

        # 8. Update global metrics
        total_reusable = sum(
            1 for s in self.strategy_repo.list_all() if s.usage_count > 0
        )
        self.metrics.set_strategies_count(self.strategy_repo.count())
        self.metrics.set_reusable_strategies(total_reusable)
        self.metrics.set_agent_learning_score(self.agent_memory.average_learning_score())
        self.metrics.set_recommendations_count(
            self.recommender.total_recommendations_generated()
        )

        # 9. Persist to RAG memory asynchronously
        summary_text = (
            f"Mission: {goal}\n"
            f"Outcome: {experience.outcome.value}\n"
            f"Duration: {experience.duration_seconds:.1f}s\n"
            f"Lessons:\n" + "\n".join(f"  {l.content}" for l in lessons)
        )
        await self.memory.persist_experience(
            experience_id=experience.experience_id,
            summary_text=summary_text,
            metadata={"mission_id": mission_id, "outcome": experience.outcome.value},
        )

        result = {
            "experience_id": experience.experience_id,
            "outcome": experience.outcome.value,
            "lessons_count": len(lessons),
            "lessons": [l.content for l in lessons],
            "patterns_detected": len(patterns),
            "agents_updated": len(experience.agents_used),
            "status": "learned",
        }
        logger.info(
            "Mission learning complete",
            experience_id=experience.experience_id,
            lessons=len(lessons),
            patterns=len(patterns),
        )
        return result

    async def recommend_strategy(self, goal: str) -> Dict[str, Any]:
        """Return the best strategy recommendation for a given goal.

        Args:
            goal: Natural language goal description.

        Returns:
            Dict with strategy content, confidence, and planner hints.
        """
        recommendations = self.recommender.recommend_for_goal(goal)
        planner_hints = self.planner_feedback.enrich_plan_request(goal)

        if recommendations:
            top = recommendations[0]
            response = {
                "recommendation": top.content,
                "confidence": top.confidence,
                "strategy_id": top.strategy_id,
                "pattern_id": top.pattern_id,
                "planner_hints": planner_hints,
                "voice_summary": (
                    f"Based on previous experience, I recommend using the strategy "
                    f"with a {top.confidence:.0%} success rate for this goal."
                ),
            }
        else:
            # Provide a generic strategy when no data is available
            keywords = goal.lower().split()
            domain = next((k for k in keywords if len(k) > 3), "planning")
            strategy = self.strategy_repo.best_strategy(domain) or self.strategy_repo.list_all()[0]
            response = {
                "recommendation": f"Use '{strategy.name}' strategy ({strategy.success_rate:.0%} success rate).",
                "confidence": strategy.success_rate,
                "strategy_id": strategy.strategy_id,
                "pattern_id": None,
                "planner_hints": planner_hints,
                "voice_summary": (
                    "I recommend a proven strategy based on domain analysis."
                ),
            }

        self.metrics.set_recommendations_count(
            self.recommender.total_recommendations_generated()
        )
        return response

    async def agent_experience(self, agent_id: str) -> Dict[str, Any]:
        """Return the accumulated experience record for a specific agent.

        Args:
            agent_id: Unique agent identifier.

        Returns:
            Dict representation of the agent's AgentExperience record.
        """
        # Ensure the record is up-to-date
        self.agent_memory.update_from_experience_store()
        record = self.agent_memory.get_experience(agent_id)

        if record:
            return record.model_dump(mode="json")

        # No data yet — return a fresh baseline
        return {
            "agent_id": agent_id,
            "total_missions": 0,
            "successful_missions": 0,
            "success_rate": 0.0,
            "preferred_strategies": [],
            "domain_expertise": {},
            "improvement_suggestions": ["No experience recorded yet."],
        }

    async def best_workflow(self, task: str) -> Dict[str, Any]:
        """Return the highest-ranked reusable workflow template for a task.

        Args:
            task: Natural language task description.

        Returns:
            Dict with workflow recommendation, confidence, and optimisations.
        """
        self.workflow_feedback.update_from_store()
        workflow_rec = self.workflow_feedback.best_workflow_for_task(task)
        ranked = self.workflow_feedback.ranked_workflows()

        return {
            "task": task,
            "recommendation": workflow_rec.get("recommendation", "No data available."),
            "confidence": workflow_rec.get("confidence", 0.0),
            "ranked_workflows": ranked[:5],
            "unreliable_workflows": self.workflow_feedback.unreliable_workflows(),
        }

    async def learning_metrics(self) -> Dict[str, Any]:
        """Return a snapshot of all Learning Engine KPIs.

        Returns:
            Dict matching the LearningMetrics schema.
        """
        # Sync all counters before snapshotting
        self.metrics.set_strategies_count(self.strategy_repo.count())
        self.metrics.set_pattern_matches(
            self.pattern_detector.count_pattern_matches()
        )
        self.metrics.set_agent_learning_score(
            self.agent_memory.average_learning_score()
        )
        self.metrics.set_recommendations_count(
            self.recommender.total_recommendations_generated()
        )
        reusable = sum(1 for s in self.strategy_repo.list_all() if s.usage_count > 0)
        self.metrics.set_reusable_strategies(reusable)

        return self.metrics.dump_summary()

    def check_health(self) -> Dict[str, Any]:
        """Return a composite health status of all sub-systems."""
        return self.health.check_health()

    # ------------------------------------------------------------------
    # Convenience helpers (used by feedback integrations)
    # ------------------------------------------------------------------

    def planner_hints(self, goal: str) -> Dict[str, Any]:
        """Return planner enrichment data for a goal (synchronous)."""
        return self.planner_feedback.enrich_plan_request(goal)

    def workflow_hints(self, task: str) -> Dict[str, Any]:
        """Return workflow optimisation hints for a task (synchronous)."""
        return self.workflow_feedback.best_workflow_for_task(task)

    def mission_summary(self) -> Dict[str, Any]:
        """Return the mission feedback summary (synchronous)."""
        return self.mission_feedback.summary()

    def safety_policy_report(self) -> Dict[str, Any]:
        """Return safety policy effectiveness report (synchronous)."""
        return self.safety_feedback.policy_effectiveness()

    def record_safety_action(
        self, action: str, approved: bool, mission_id: Optional[str] = None
    ) -> None:
        """Record a safety approval decision for learning."""
        self.safety_feedback.record_action(action, approved, mission_id)
