"""Unit and integration tests for AI Software Copilot Engine and SDLC components.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.copilot.copilot_engine import CopilotEngine
from app.ai.copilot.mock_provider import MockCopilotProvider
from app.ai.copilot.models import (
    ArchitectureStyle,
    CopilotState,
    ProjectLanguage,
    SDLCStage,
)


@pytest.mark.anyio
async def test_requirement_analyzer():
    engine = CopilotEngine()
    reqs = await engine.requirement_analyzer.analyze_requirements("Build a REST API with FastAPI and React")
    assert reqs.project_name == "NovaProject"
    assert len(reqs.functional_requirements) > 0
    assert "FastAPI" in reqs.technology_preferences


@pytest.mark.anyio
async def test_architecture_engine():
    engine = CopilotEngine()
    reqs = await engine.requirement_analyzer.analyze_requirements("Build microservices backend")
    arch = await engine.architecture_engine.design_architecture(reqs)
    assert arch.style == ArchitectureStyle.MICROSERVICES
    assert "api_gateway_service" in arch.service_boundaries


@pytest.mark.anyio
async def test_technology_selector():
    engine = CopilotEngine()
    reqs = await engine.requirement_analyzer.analyze_requirements("Spring Boot Java backend")
    arch = await engine.architecture_engine.design_architecture(reqs)
    stack = await engine.technology_selector.select_technologies(reqs, arch)
    assert "java" in stack.languages
    assert "Spring Boot" in stack.frameworks


@pytest.mark.anyio
async def test_code_generator():
    engine = CopilotEngine()
    reqs = await engine.requirement_analyzer.analyze_requirements("Build app")
    arch = await engine.architecture_engine.design_architecture(reqs)
    stack = await engine.technology_selector.select_technologies(reqs, arch)
    files = await engine.code_generator.generate_code(reqs, arch, stack)
    assert len(files) >= 5
    paths = [f.path for f in files]
    assert "apps/backend/main.py" in paths
    assert "Dockerfile" in paths


@pytest.mark.anyio
async def test_code_understanding():
    engine = CopilotEngine()
    res = await engine.analyze_project("c:\\Projects\\Nova-AI")
    assert res["architecture_pattern"] == "Modular Monolith"
    assert len(res["entry_points"]) > 0


@pytest.mark.anyio
async def test_debug_engine():
    engine = CopilotEngine()
    bug = await engine.debug_project("main.py", "KeyError: 'user_id'")
    assert bug.verified is True
    assert bug.title == "KeyError in Dictionary Access"


@pytest.mark.anyio
async def test_refactor_engine():
    engine = CopilotEngine()
    ref = await engine.refactor_project("main.py", "Optimize database query performance")
    assert ref.target_file == "main.py"
    assert len(ref.architectural_improvements) > 0


@pytest.mark.anyio
async def test_test_engine():
    engine = CopilotEngine()
    rpt = await engine.test_project("c:\\Projects\\Nova-AI")
    assert rpt.total_tests == 24
    assert rpt.coverage_percent > 90.0


@pytest.mark.anyio
async def test_deployment_engine():
    engine = CopilotEngine()
    cfg = await engine.deploy_project("c:\\Projects\\Nova-AI")
    assert cfg.target == "local_docker_compose"
    assert "backend" in cfg.container_spec


@pytest.mark.anyio
async def test_review_and_document_engine():
    engine = CopilotEngine()
    rev = await engine.review_project("c:\\Projects\\Nova-AI")
    assert rev.score >= 90.0
    docs = await engine.document_project("NovaProject")
    assert len(docs.readme_md) > 0


@pytest.mark.anyio
async def test_copilot_create_project_end_to_end():
    engine = CopilotEngine()
    proj = await engine.create_project("Build an ERP system with FastAPI and React", name="ERPProject")
    assert proj.name == "ERPProject"
    assert proj.stage == SDLCStage.COMPLETED
    assert len(proj.files) >= 5


@pytest.mark.anyio
async def test_mock_copilot_provider():
    mock = MockCopilotProvider()
    proj = await mock.create_project("Test prompt", name="MockProj")
    assert proj.name == "MockProj"
    health = await mock.check_health()
    assert health.is_healthy is True
