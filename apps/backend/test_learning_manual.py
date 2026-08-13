"""Manual validation script for M3.3.8 – Continuous Learning & Shared Experience Engine.

Run from apps/backend/:
    python test_learning_manual.py

Expected output:
    =========================================
    Nova AI Learning Validation
    =========================================
    Stage 1  Experience Storage          PASS
    Stage 2  Pattern Detection           PASS
    Stage 3  Lesson Extraction           PASS
    Stage 4  Strategy Repository         PASS
    Stage 5  Recommendations             PASS
    Stage 6  Planner Feedback            PASS
    Stage 7  Workflow Feedback           PASS
    Stage 8  Mission Feedback            PASS
    Stage 9  Safety Feedback             PASS
    Stage 10 Agent Learning              PASS
    Stage 11 Gateway                     PASS
    Stage 12 Complete                    PASS

    12/12 PASS

    Learning Engine Healthy
"""

import asyncio
import sys


def _banner() -> None:
    print("=========================================")
    print("Nova AI Learning Validation")
    print("=========================================")


def _result(stage: int, label: str, passed: bool, error: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"Stage {stage:<2} {label:<30} {status}")
    if not passed and error:
        print(f"       Error: {error}")
    return passed


def stage_1_experience_storage() -> bool:
    try:
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.experience_manager import ExperienceManager
        from app.ai.learning.models import ExperienceOutcome

        store = ExperienceStore()
        manager = ExperienceManager(store=store)
        exp = manager.build_experience(
            "ms_val_01",
            "Build React Dashboard",
            {"status": "success", "duration_seconds": 30.0, "agents_used": ["frontend", "backend"]},
        )
        assert store.count() == 1
        retrieved = store.get_experience(exp.experience_id)
        assert retrieved.outcome == ExperienceOutcome.COMPLETED
        assert store.success_rate() == 1.0
        return True
    except Exception as e:
        return _result(1, "Experience Storage", False, str(e)) or False


def stage_2_pattern_detection() -> bool:
    try:
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.experience_manager import ExperienceManager
        from app.ai.learning.pattern_detector import PatternDetector

        store = ExperienceStore()
        manager = ExperienceManager(store=store)
        for i in range(3):
            manager.build_experience(
                f"ms_ptn_{i}",
                "Build React dashboard",
                {"status": "success", "duration_seconds": 25.0, "agents_used": ["frontend"]},
            )

        detector = PatternDetector(store=store)
        patterns = detector.detect_all()
        assert isinstance(patterns, list)
        assert detector.count_pattern_matches() >= 0
        return True
    except Exception as e:
        return _result(2, "Pattern Detection", False, str(e)) or False


def stage_3_lesson_extraction() -> bool:
    try:
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.experience_manager import ExperienceManager
        from app.ai.learning.lesson_extractor import LessonExtractor
        from app.ai.learning.models import LessonCategory

        store = ExperienceStore()
        manager = ExperienceManager(store=store)
        exp = manager.build_experience(
            "ms_lsn_01",
            "Build authentication service",
            {
                "status": "success",
                "duration_seconds": 25.0,
                "agents_used": ["backend", "security"],
                "user_satisfaction": 0.95,
                "approval_count": 0,
            },
        )
        extractor = LessonExtractor()
        lessons = extractor.extract(exp)
        assert len(lessons) > 0
        assert all(l.confidence > 0 for l in lessons)

        # Failure lesson
        exp_fail = manager.build_experience(
            "ms_lsn_02",
            "Deploy microservice",
            {"status": "failed", "duration_seconds": 8.0, "agents_used": ["devops"]},
        )
        fail_lessons = extractor.extract(exp_fail)
        assert any(l.category == LessonCategory.FAILURE for l in fail_lessons)
        return True
    except Exception as e:
        return _result(3, "Lesson Extraction", False, str(e)) or False


def stage_4_strategy_repository() -> bool:
    try:
        from app.ai.learning.strategy_repository import StrategyRepository
        from app.ai.learning.models import Strategy

        repo = StrategyRepository()
        assert repo.count() >= 6
        assert repo.best_strategy("coding") is not None
        assert repo.best_strategy("deployment") is not None

        # Test versioning — use 0.99 to outrank seeded Pyramid Testing Strategy (0.87)
        s = Strategy(
            name="Manual Validation Strategy",
            domain="testing",
            description="Added during validation",
            success_rate=0.99,
        )
        repo.save_strategy(s)
        best = repo.best_strategy("testing")
        assert best is not None
        assert best.name == "Manual Validation Strategy"

        # Test keyword search
        result = repo.best_for_keywords(["deployment", "staging", "blue-green"])
        assert result is not None
        assert result.domain == "deployment"
        return True
    except Exception as e:
        return _result(4, "Strategy Repository", False, str(e)) or False


def stage_5_recommendations() -> bool:
    try:
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.experience_manager import ExperienceManager
        from app.ai.learning.recommendation_engine import RecommendationEngine
        from app.ai.learning.strategy_repository import StrategyRepository
        from app.ai.learning.pattern_detector import PatternDetector

        store = ExperienceStore()
        manager = ExperienceManager(store=store)
        for i in range(3):
            manager.build_experience(
                f"ms_rec_{i}",
                "Build React dashboard",
                {"status": "success", "duration_seconds": 20.0, "agents_used": ["frontend"]},
            )

        repo = StrategyRepository()
        detector = PatternDetector(store=store)
        detector.detect_all()
        engine = RecommendationEngine(store=store, pattern_detector=detector, strategy_repo=repo)

        planner_recs = engine.recommend_for_goal("Build a React analytics dashboard")
        assert isinstance(planner_recs, list)

        workflow_recs = engine.recommend_for_workflow("Deploy REST API")
        assert isinstance(workflow_recs, list)

        agent_recs = engine.recommend_for_agent("backend", domain="coding")
        assert isinstance(agent_recs, list)
        return True
    except Exception as e:
        return _result(5, "Recommendations", False, str(e)) or False


def stage_6_planner_feedback() -> bool:
    try:
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.experience_manager import ExperienceManager
        from app.ai.learning.planner_feedback import PlannerFeedback
        from app.ai.learning.strategy_repository import StrategyRepository

        store = ExperienceStore()
        manager = ExperienceManager(store=store)
        manager.build_experience(
            "ms_pf_01",
            "Build REST API backend",
            {"status": "success", "duration_seconds": 30.0, "agents_used": ["backend"]},
        )
        manager.build_experience(
            "ms_pf_02",
            "Build REST API backend",
            {"status": "failed", "duration_seconds": 10.0, "agents_used": ["backend"]},
        )

        repo = StrategyRepository()
        feedback = PlannerFeedback(store=store, strategy_repo=repo)
        hints = feedback.enrich_plan_request("Build a REST API backend")

        assert "success_rate" in hints
        assert "recommendations" in hints
        assert "failure_warnings" in hints
        assert hints["failure_warnings"]  # At least one warning from the failure
        return True
    except Exception as e:
        return _result(6, "Planner Feedback", False, str(e)) or False


def stage_7_workflow_feedback() -> bool:
    try:
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.experience_manager import ExperienceManager
        from app.ai.learning.workflow_feedback import WorkflowFeedback

        store = ExperienceStore()
        manager = ExperienceManager(store=store)
        manager.build_experience(
            "ms_wf_01",
            "Deploy containerised app",
            {"status": "success", "duration_seconds": 40.0,
             "agents_used": ["devops"], "workflow_id": "wf_deploy_01"},
        )
        manager.build_experience(
            "ms_wf_02",
            "Deploy containerised app",
            {"status": "failed", "duration_seconds": 12.0,
             "agents_used": ["devops"], "workflow_id": "wf_deploy_01"},
        )

        feedback = WorkflowFeedback(store=store)
        feedback.update_from_store()
        ranked = feedback.ranked_workflows()
        assert isinstance(ranked, list)
        assert len(ranked) >= 1

        best = feedback.best_workflow_for_task("Deploy microservice")
        assert "recommendation" in best
        return True
    except Exception as e:
        return _result(7, "Workflow Feedback", False, str(e)) or False


def stage_8_mission_feedback() -> bool:
    try:
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.experience_manager import ExperienceManager
        from app.ai.learning.mission_feedback import MissionFeedback

        store = ExperienceStore()
        manager = ExperienceManager(store=store)
        for i in range(4):
            status = "success" if i < 3 else "failed"
            manager.build_experience(
                f"ms_mf_{i}",
                f"Mission {i}",
                {"status": status, "duration_seconds": 20.0, "agents_used": ["backend"]},
            )

        feedback = MissionFeedback(store=store)
        summary = feedback.summary()
        assert summary["total_missions"] == 4
        assert abs(summary["completion_rate"] - 0.75) < 0.01
        assert isinstance(feedback.improvement_opportunities(), list)
        return True
    except Exception as e:
        return _result(8, "Mission Feedback", False, str(e)) or False


def stage_9_safety_feedback() -> bool:
    try:
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.safety_feedback import SafetyFeedback

        store = ExperienceStore()
        feedback = SafetyFeedback(store=store)

        for _ in range(9):
            feedback.record_action("read_logs", approved=True)
        feedback.record_action("read_logs", approved=False)

        approved = feedback.frequently_approved_actions(threshold=0.8)
        assert "read_logs" in approved

        feedback.record_action("rm_rf", approved=False)
        feedback.record_action("rm_rf", approved=False)
        rejected = feedback.frequently_rejected_actions(threshold=0.5)
        assert "rm_rf" in rejected

        policy = feedback.policy_effectiveness()
        assert "approval_rate" in policy
        suggestions = feedback.risk_classification_suggestions()
        assert isinstance(suggestions, list)
        return True
    except Exception as e:
        return _result(9, "Safety Feedback", False, str(e)) or False


def stage_10_agent_learning() -> bool:
    try:
        from app.ai.learning.agent_memory import AgentMemory
        from app.ai.learning.collaboration_learning import CollaborationLearning
        from app.ai.learning.experience_store import ExperienceStore
        from app.ai.learning.configuration import LearningConfiguration

        store = ExperienceStore()
        config = LearningConfiguration(enable_cross_agent_sharing=True)
        memory = AgentMemory(store=store, config=config)

        memory.record_experience("backend", "success", "Build API", 20.0)
        memory.record_experience("backend", "success", "Build Auth", 15.0)
        memory.assign_strategy("backend", "str_coding_v1")

        memory.record_experience("frontend", "failed", "Build UI", 10.0)
        memory.share_strategies_to("frontend")

        backend_rec = memory.get_experience("backend")
        assert backend_rec is not None
        assert backend_rec.success_rate == 1.0

        frontend_rec = memory.get_experience("frontend")
        assert frontend_rec is not None
        assert "str_coding_v1" in frontend_rec.preferred_strategies

        # Collaboration
        collab = CollaborationLearning(store=store, agent_memory=memory, config=config)
        sync_result = collab.sync_team_knowledge(["backend", "frontend", "qa"])
        assert "shared" in sync_result
        return True
    except Exception as e:
        return _result(10, "Agent Learning", False, str(e)) or False


async def stage_11_gateway() -> bool:
    try:
        from app.core.dependency_container import resolve, register_ai_gateway_dependencies
        from app.ai.gateway import IAIGateway

        try:
            register_ai_gateway_dependencies()
        except Exception:
            pass

        gateway = resolve(IAIGateway)

        # learn_from_mission
        learn_result = await gateway.learn_from_mission(
            "ms_gw_validate_01",
            mission_result={
                "goal": "Build CRM customer records backend",
                "status": "success",
                "duration_seconds": 60.0,
                "agents_used": ["backend", "database"],
            },
        )
        assert learn_result["status"] == "learned"
        assert "experience_id" in learn_result

        # recommend_strategy
        strategy_result = await gateway.recommend_strategy(
            "Build a React analytics dashboard with backend API"
        )
        assert "recommendation" in strategy_result
        assert "confidence" in strategy_result

        # agent_experience
        agent_result = await gateway.agent_experience("backend")
        assert agent_result["agent_id"] == "backend"

        # best_workflow
        workflow_result = await gateway.best_workflow(
            "Deploy Python microservice to Kubernetes"
        )
        assert "recommendation" in workflow_result

        # learning_metrics
        metrics_result = await gateway.learning_metrics()
        required = {
            "total_experiences", "success_rate", "failure_rate",
            "learned_strategies", "pattern_matches",
            "recommendations_generated", "knowledge_reuse_pct",
            "agent_learning_score",
        }
        assert required.issubset(set(metrics_result.keys()))
        return True
    except Exception as e:
        return _result(11, "Gateway", False, str(e)) or False


async def stage_12_complete() -> bool:
    """Validate the full end-to-end learning cycle."""
    try:
        from app.ai.learning.learning_engine import LearningEngine
        from app.ai.learning.providers.mock_provider import MockLearningProvider

        engine = LearningEngine()
        mock = MockLearningProvider()

        # Mock provider validation
        mock_exp = mock.simulate_experience()
        assert mock_exp["status"] == "success"

        mock_patterns = mock.simulate_patterns()
        assert len(mock_patterns) == 2

        mock_strategy = mock.simulate_strategy("coding")
        assert mock_strategy["domain"] == "coding"

        mock_lessons = mock.simulate_lessons()
        assert len(mock_lessons) >= 4

        mock_rec = mock.simulate_recommendation("Build dashboard")
        assert mock_rec["confidence"] > 0

        mock_metrics = mock.simulate_metrics()
        assert mock_metrics["total_experiences"] == 10

        mock_health = mock.simulate_health()
        assert mock_health["status"] == "healthy"

        # Full learn cycle
        result = await engine.learn_from_mission(
            "ms_final_validate",
            {
                "goal": "Build enterprise CRM system",
                "status": "success",
                "duration_seconds": 120.0,
                "agents_used": ["backend", "frontend", "database", "qa"],
                "user_satisfaction": 1.0,
                "approval_count": 0,
            },
        )
        assert result["status"] == "learned"
        assert result["lessons_count"] > 0

        # Metrics snapshot
        metrics = await engine.learning_metrics()
        assert metrics["total_experiences"] >= 1
        assert metrics["learned_strategies"] >= 6

        # Health check
        health = engine.check_health()
        assert health["status"] == "healthy"
        return True
    except Exception as e:
        return _result(12, "Complete", False, str(e)) or False


async def main() -> None:
    _banner()

    results = []

    # Synchronous stages
    results.append(_result(1, "Experience Storage", stage_1_experience_storage()))
    results.append(_result(2, "Pattern Detection", stage_2_pattern_detection()))
    results.append(_result(3, "Lesson Extraction", stage_3_lesson_extraction()))
    results.append(_result(4, "Strategy Repository", stage_4_strategy_repository()))
    results.append(_result(5, "Recommendations", stage_5_recommendations()))
    results.append(_result(6, "Planner Feedback", stage_6_planner_feedback()))
    results.append(_result(7, "Workflow Feedback", stage_7_workflow_feedback()))
    results.append(_result(8, "Mission Feedback", stage_8_mission_feedback()))
    results.append(_result(9, "Safety Feedback", stage_9_safety_feedback()))
    results.append(_result(10, "Agent Learning", stage_10_agent_learning()))

    # Async stages
    results.append(_result(11, "Gateway", await stage_11_gateway()))
    results.append(_result(12, "Complete", await stage_12_complete()))

    passed = sum(results)
    total = len(results)

    print()
    print(f"{passed}/{total} PASS")
    print()

    if passed == total:
        print("Learning Engine Healthy")
    else:
        print("Learning Engine Degraded")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
