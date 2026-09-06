"""Unit and integration tests for AI Software Copilot Engine and SDLC components.
"""

import pytest
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


@pytest.mark.anyio
async def test_copilot_orchestrator_modes_and_routing():
    from app.ai.copilot.orchestrator import CopilotOrchestrator
    from app.ai.copilot.models import CopilotMode, CopilotRequest

    orchestrator = CopilotOrchestrator()

    # 1. Test EXPLAIN mode
    req_explain = CopilotRequest(
        user_prompt="How do I save in VS Code?",
        mode=CopilotMode.EXPLAIN,
        target_app="VS Code",
    )
    res_explain = await orchestrator.process_request(req_explain)
    assert res_explain.success is True
    assert res_explain.mode == CopilotMode.EXPLAIN
    assert res_explain.app_context.app_name == "VS Code"
    assert "Explanation for 'VS Code'" in res_explain.explanation
    assert len(res_explain.execution_results) == 0

    # 2. Test GUIDE mode
    req_guide = CopilotRequest(
        user_prompt="Show me how to format code",
        mode=CopilotMode.GUIDE,
        target_app="VS Code",
    )
    res_guide = await orchestrator.process_request(req_guide)
    assert res_guide.success is True
    assert res_guide.mode == CopilotMode.GUIDE
    assert len(res_guide.guide_steps) > 0
    assert len(res_guide.execution_results) == 0

    # 3. Test EXECUTE mode (successful real execution path)
    req_exec = CopilotRequest(
        user_prompt="Save File",
        mode=CopilotMode.EXECUTE,
        target_app="VS Code",
        parameters={"action_type": "click", "target_label": "Save Button"},
    )
    res_exec = await orchestrator.process_request(req_exec)
    assert res_exec.success is True
    assert res_exec.mode == CopilotMode.EXECUTE
    assert len(res_exec.execution_results) == 1
    assert res_exec.execution_results[0].success is True
    assert len(res_exec.verification_results) == 1
    assert res_exec.verification_results[0].verified is True

    # 4. Test EXECUTE mode with permission enforcement (sensitive action)
    req_sensitive = CopilotRequest(
        user_prompt="Modify Registry",
        mode=CopilotMode.EXECUTE,
        target_app="VS Code",
        parameters={"action_type": "registry_write"},
    )
    res_sensitive = await orchestrator.process_request(req_sensitive)
    assert res_sensitive.success is False
    assert "requires explicit human approval" in res_sensitive.status_message or "blocked" in res_sensitive.status_message.lower()

    # 5. Test EXECUTE mode with failed execution / unsupported action
    req_unsupported = CopilotRequest(
        user_prompt="Do Unsupported Action",
        mode=CopilotMode.EXECUTE,
        target_app="VS Code",
        parameters={"action_type": "unsupported_action_type"},
    )
    res_unsupported = await orchestrator.process_request(req_unsupported)
    assert res_unsupported.success is False
    assert res_unsupported.execution_results[0].success is False

    # 6. Test Unknown Application & Missing Context
    req_unknown = CopilotRequest(
        user_prompt="Explain NonExistentApp",
        mode=CopilotMode.EXPLAIN,
        target_app="Unknown",
    )
    res_unknown = await orchestrator.process_request(req_unknown)
    assert res_unknown.success is True
    assert res_unknown.app_context.app_name == "Unknown"
    assert res_unknown.app_context.process_id is None

    # 7. Test Specialized Adapter Selection (Blender)
    req_blender = CopilotRequest(
        user_prompt="Create Cube",
        mode=CopilotMode.EXECUTE,
        target_app="Blender",
        parameters={"action_type": "create_object", "target_label": "Cube"},
    )
    res_blender = await orchestrator.process_request(req_blender)
    assert res_blender.mode == CopilotMode.EXECUTE
    assert res_blender.app_context.app_name == "Blender"


@pytest.mark.anyio
async def test_blender_copilot_specialization():
    from app.ai.desktop_automation.application_adapter import BlenderApplicationAdapter
    from app.ai.desktop_automation.blender_adapter import BlenderActionValidator, BlenderActionValidationError
    from app.ai.desktop_automation.exceptions import ApprovalRequiredError
    from app.ai.desktop_automation.models import AutomationAction
    from app.ai.copilot.orchestrator import CopilotOrchestrator
    from app.ai.copilot.models import CopilotMode, CopilotRequest

    adapter = BlenderApplicationAdapter()

    # 1. Blender Detection Test
    is_detected = await adapter.detect()
    assert isinstance(is_detected, bool)

    # 2. Structured Action Validation Test
    act_create = AutomationAction(action_type="create_object", target_label="RedCube", selector={"primitive": "cube", "location": [1.0, 2.0, 3.0]})
    validated = BlenderActionValidator.validate_action(act_create)
    assert validated["name"] == "RedCube"
    assert validated["primitive"] == "cube"
    assert validated["location"] == (1.0, 2.0, 3.0)

    # 3. Invalid Primitive Rejection Test
    act_invalid = AutomationAction(action_type="create_object", target_label="Bad", selector={"primitive": "invalid_mesh_type"})
    with pytest.raises(BlenderActionValidationError):
        BlenderActionValidator.validate_action(act_invalid)

    # 4. No Arbitrary Python Execution Test
    act_raw = AutomationAction(action_type="raw_python", target_label="import os; os.system('calc')")
    res_raw = await adapter.execute(act_raw)
    assert res_raw.success is False
    assert "forbidden" in res_raw.error_message.lower()

    # 5. Security Rejection Test
    act_sensitive = AutomationAction(action_type="registry_write", target_label="HKLM")
    with pytest.raises(ApprovalRequiredError):
        await adapter.execute(act_sensitive)

    # 6. Unsupported Operation Rejection Test
    act_unsupported = AutomationAction(action_type="unsupported_blender_op", target_label="Target")
    res_unsupported = await adapter.execute(act_unsupported)
    assert res_unsupported.success is False
    assert "not supported" in res_unsupported.error_message.lower()

    # 7. Execution Failure / Blender Unavailable Test
    act_cube = AutomationAction(action_type="create_object", target_label="Cube", selector={"primitive": "cube"})
    res_cube = await adapter.execute(act_cube)
    assert isinstance(res_cube.success, bool)

    # 8. Verification Failure Test on Failed Action
    ver_failed = await adapter.verify(act_unsupported, res_unsupported)
    assert ver_failed.verified is False
    assert ver_failed.confidence == 0.0

    # 9. Copilot Orchestrator End-to-End Blender Test
    orchestrator = CopilotOrchestrator()
    req_blender_create = CopilotRequest(
        user_prompt="Create 3D Cube",
        mode=CopilotMode.EXECUTE,
        target_app="Blender",
        parameters={"action_type": "create_object", "target_label": "MyCube", "primitive": "cube"},
    )
    res_copilot = await orchestrator.process_request(req_blender_create)
    assert res_copilot.mode == CopilotMode.EXECUTE
    assert res_copilot.app_context.app_name == "Blender"
    assert len(res_copilot.execution_results) == 1
