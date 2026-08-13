"""Unit and integration tests for Autonomous Self-Improvement & Adaptive Intelligence Engine.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
from app.ai.self_improvement.mock_provider import MockSelfImprovementProvider
from app.ai.self_improvement.models import (
    EvaluationCycle,
    OptimizationStatus,
    RegressionStatus,
)


@pytest.mark.anyio
async def test_self_improvement_execution():
    engine = UniversalSelfImprovementEngine()
    res = await engine.self_improve()
    assert res["status"] == "SUCCESS"
    assert res["evaluations"]["overall_score"] > 0.90
    assert res["experiences_distilled"] >= 1


@pytest.mark.anyio
async def test_performance_analyzer_and_reports():
    engine = UniversalSelfImprovementEngine()
    report = await engine.performance_report()
    assert "kernel" in report
    assert report["kernel"]["latency_ms"] > 0
    assert report["user_rating"] >= 4.0


@pytest.mark.anyio
async def test_workflow_and_agent_optimizers():
    engine = UniversalSelfImprovementEngine()
    recs = await engine.workflow_recommendations()
    assert len(recs) >= 1
    assert "impact" in recs[0]

    cards = await engine.agent_scorecard()
    assert len(cards) >= 3
    assert cards[0]["role"] == "software_engineer"


@pytest.mark.anyio
async def test_benchmark_and_quality_engines():
    engine = UniversalSelfImprovementEngine()
    bench = await engine.benchmark_report()
    assert bench["overall_score"] >= 0.90

    qual = await engine.quality_report()
    assert qual["status"] == RegressionStatus.NORMAL.value


@pytest.mark.anyio
async def test_experience_distiller_and_skills_evolution():
    engine = UniversalSelfImprovementEngine()
    pkg = engine.experience_distiller.distill_experience("Test Workflow", ["Step 1", "Step 2"])
    assert pkg.reusable_skill_id == "skill_test_workflow"

    evolve = engine.skill_evolution.evaluate_workflow_frequency("Deploy FastAPI", execution_count=5)
    assert evolve["should_evolve"] is True


@pytest.mark.anyio
async def test_adaptive_behavior_and_goal_optimizer():
    engine = UniversalSelfImprovementEngine()
    settings = await engine.adaptive_settings()
    assert "style" in settings
    assert settings["style"]["safety_lock_verified"] is True
    assert "Python" in settings["profile"]["primary_tech_stack"]


@pytest.mark.anyio
async def test_feedback_and_knowledge_refiner():
    engine = UniversalSelfImprovementEngine()
    engine.feedback_engine.record_feedback("mission_101", 5.0, "Great execution!")
    rating = engine.feedback_engine.get_average_rating()
    assert rating == 5.0

    refined = engine.knowledge_refiner.refine_knowledge_base()
    assert refined["vector_index_quality_score"] > 0.90


@pytest.mark.anyio
async def test_self_improvement_health_and_metrics():
    engine = UniversalSelfImprovementEngine()
    await engine.self_improve()

    health = await engine.check_health()
    assert health.is_healthy is True
    assert health.total_optimizations_applied >= 1

    metrics = await engine.get_metrics()
    assert metrics.total_evaluations >= 1


@pytest.mark.anyio
async def test_mock_self_improvement_provider():
    mock = MockSelfImprovementProvider()
    res = await mock.mock_self_improve()
    assert res["status"] == "SUCCESS"

    bench = await mock.mock_benchmark()
    assert bench.overall_score == 0.98
