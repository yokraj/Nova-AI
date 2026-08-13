"""Unit and integration tests for Universal Knowledge, Research & Reasoning Engine.
"""

import pytest
from app.ai.research.research_engine import UniversalResearchEngine
from app.ai.research.mock_provider import MockResearchProvider
from app.ai.research.models import (
    ConfidenceLevel,
    EvidenceLevel,
    ResearchState,
)


@pytest.mark.anyio
async def test_research_planner():
    engine = UniversalResearchEngine()
    plan = await engine.planner.create_plan("Artificial Intelligence Agents", mode="deep")
    assert plan.topic == "Artificial Intelligence Agents"
    assert len(plan.sub_questions) >= 4
    assert plan.complexity == "high"


@pytest.mark.anyio
async def test_knowledge_collector_and_search():
    engine = UniversalResearchEngine()
    sources = await engine.search("FastAPI framework architecture")
    assert len(sources) >= 3
    for s in sources:
        assert len(s.title) > 0
        assert s.trust_score > 0.0


@pytest.mark.anyio
async def test_verification_and_reasoning_engines():
    engine = UniversalResearchEngine()
    sources = await engine.search("React 19 Server Components")
    verification = await engine.verifier.verify_claim("React Server Components improve initial page load", sources)
    assert verification.verification_score >= 0.80
    assert verification.confidence == ConfidenceLevel.HIGH

    reasoning = await engine.reasoner.reason("React 19 Server Components", [verification])
    assert len(reasoning.conclusions) >= 1
    assert "React 19" in reasoning.topic


@pytest.mark.anyio
async def test_knowledge_graph():
    engine = UniversalResearchEngine()
    summary = await engine.knowledge_graph()
    assert summary["nodes_count"] >= 3
    assert summary["edges_count"] >= 2

    related = engine.graph.get_related_nodes("repo_nova_ai")
    assert len(related) >= 2


@pytest.mark.anyio
async def test_repository_and_document_intelligence():
    engine = UniversalResearchEngine()
    repo_sum = await engine.analyze_repository("c:\\Projects\\Nova-AI")
    assert repo_sum.name == "Nova-AI"
    assert "Python" in repo_sum.languages
    assert "FastAPI" in repo_sum.frameworks

    doc_sum = await engine.analyze_document("./docs/architecture.pdf")
    assert doc_sum.format == "PDF"
    assert len(doc_sum.paragraphs) >= 3
    assert len(doc_sum.tables) >= 1


@pytest.mark.anyio
async def test_report_and_citation_engines():
    engine = UniversalResearchEngine()
    report = await engine.research("Kubernetes Orchestration Best Practices")
    assert report.topic == "Kubernetes Orchestration Best Practices"
    assert len(report.executive_summary) > 0
    assert len(report.citations) >= 1
    assert len(report.voice_summary) > 0


@pytest.mark.anyio
async def test_research_memory_and_resumption():
    engine = UniversalResearchEngine()
    await engine.research("Quantum Computing Algorithms")
    history = await engine.research_history()
    assert len(history) >= 1

    resumed_report = await engine.continue_research("Quantum Computing Algorithms", "Focus on Shor's Algorithm")
    assert "Quantum Computing" in resumed_report.topic


@pytest.mark.anyio
async def test_knowledge_packages():
    engine = UniversalResearchEngine()
    pkg = await engine.knowledge_package("React")
    assert pkg.topic == "React"
    assert len(pkg.examples) >= 2
    assert len(pkg.best_practices) >= 2


@pytest.mark.anyio
async def test_research_agent_and_health():
    engine = UniversalResearchEngine()
    agent_res = await engine.agent.execute_research_task("Analyze AI Agents")
    assert agent_res["status"] == "COMPLETED"

    await engine.research("Analyze AI Agents")

    health = await engine.check_health()
    assert health.is_healthy is True
    assert health.research_state == ResearchState.COMPLETED

    metrics = await engine.get_metrics()
    assert metrics.reports_generated >= 1



@pytest.mark.anyio
async def test_mock_research_provider():
    mock = MockResearchProvider()
    sources = await mock.mock_search("test query")
    assert len(sources) == 1
    report = await mock.mock_generate_report("test topic")
    assert report.topic == "test topic"
