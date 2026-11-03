"""Comprehensive Test Suite for V2 Unified Agent Execution Engine.

Tests:
1. Scenario 1: Deterministic math calculation (e.g. 19 * 37 = 703)
2. Scenario 2: Document intelligence inspection (README.md)
3. Scenario 3: Python AST code analysis (apps/backend/app/main.py)
4. Scenario 4: Real Windows desktop application launch & verification (Notepad)
5. Scenario 5: Multi-step target interaction ("open Notepad, create meeting.txt and write...")
6. Scenario 6: Security & permission gate rejection on sensitive actions
7. Scenario 7: Honest failure reporting on missing file
8. Scenario 8: Task cancellation support
9. Scenario 9: Workspace path traversal security rejection
"""

import sys
from pathlib import Path
import pytest

# Ensure backend directory is in sys.path for direct execution and IDE language servers
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.intelligence.agent_execution_engine import (
    AgentExecutionEngine,
    TaskIntent,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if not BASE_DIR.exists() or not (BASE_DIR / "apps").exists():
    BASE_DIR = Path(r"C:\Projects\Nova-AI")


@pytest.fixture
def engine() -> AgentExecutionEngine:
    return AgentExecutionEngine()


@pytest.mark.asyncio
async def test_scenario_1_deterministic_math(engine: AgentExecutionEngine):
    prompt = "What is 19 multiplied by 37? Explain step by step."
    analysis = engine.understand_task(prompt)
    assert analysis["intent"] == TaskIntent.CALCULATION
    
    plan = engine.create_plan(prompt, analysis)
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "calculate_math"
    
    report = await engine.execute_plan(plan)
    assert report.status == "SUCCEEDED"
    assert report.verified is True
    assert "703" in report.final_output


@pytest.mark.asyncio
async def test_scenario_2_document_inspection(engine: AgentExecutionEngine):
    prompt = "Please inspect and summarize README.md"
    analysis = engine.understand_task(prompt)
    assert analysis["intent"] == TaskIntent.DOCUMENT_INSPECTION
    
    plan = engine.create_plan(prompt, analysis)
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "read_document"
    
    report = await engine.execute_plan(plan)
    assert report.status == "SUCCEEDED"
    assert report.verified is True
    assert "README.md" in report.final_output


@pytest.mark.asyncio
async def test_scenario_3_python_ast_analysis(engine: AgentExecutionEngine):
    prompt = "Analyze the code in apps/backend/app/main.py and find functions"
    analysis = engine.understand_task(prompt)
    assert analysis["intent"] == TaskIntent.CODE_ANALYSIS
    
    plan = engine.create_plan(prompt, analysis)
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "analyze_code"
    
    report = await engine.execute_plan(plan)
    assert report.status == "SUCCEEDED"
    assert report.verified is True
    assert "root" in report.final_output or "lifespan" in report.final_output


@pytest.mark.asyncio
async def test_scenario_4_open_and_verify_application(engine: AgentExecutionEngine):
    prompt = "Open Notepad on my workstation"
    analysis = engine.understand_task(prompt)
    assert analysis["intent"] == TaskIntent.DESKTOP_OPERATION
    
    plan = engine.create_plan(prompt, analysis)
    assert len(plan.steps) == 2
    assert plan.steps[0].tool_name == "open_application"
    assert plan.steps[1].tool_name == "verify_application"
    
    try:
        report = await engine.execute_plan(plan)
        assert report.status == "SUCCEEDED"
        assert report.verified is True
        assert report.steps_succeeded == 2
        
        # Verify Notepad is physically running
        assert engine.tools.launcher.is_application_running("notepad") is True
    finally:
        # Terminate notepad
        engine.tools.launcher.terminate_application("notepad")


@pytest.mark.asyncio
async def test_scenario_5_target_multi_step_workflow(engine: AgentExecutionEngine):
    prompt = "Nova, open Notepad, create a file called meeting.txt and write Tomorrow's meeting is at 10 AM."
    analysis = engine.understand_task(prompt)
    assert analysis["intent"] == TaskIntent.MULTI_STEP_TASK
    assert analysis["entities"]["app_name"].lower() == "notepad"
    assert analysis["entities"]["file_path"] == "meeting.txt"
    assert "Tomorrow's meeting is at 10 AM" in analysis["entities"]["content"]
    
    plan = engine.create_plan(prompt, analysis)
    assert len(plan.steps) == 3
    assert plan.steps[0].tool_name == "open_application"
    assert plan.steps[1].tool_name == "create_file"
    assert plan.steps[2].tool_name == "verify_application"
    
    test_file = BASE_DIR / "meeting.txt"
    try:
        report = await engine.execute_plan(plan)
        assert report.status == "SUCCEEDED"
        assert report.verified is True
        assert report.steps_succeeded == 3
        
        # Verify real physical side effects on disk and OS
        assert test_file.exists() is True
        assert "Tomorrow's meeting is at 10 AM" in test_file.read_text(encoding="utf-8")
        assert engine.tools.launcher.is_application_running("notepad") is True
        assert "meeting.txt" in report.final_output
    finally:
        if test_file.exists():
            test_file.unlink()
        engine.tools.launcher.terminate_application("notepad")


@pytest.mark.asyncio
async def test_scenario_6_security_permission_gate(engine: AgentExecutionEngine):
    # Action requiring human approval without is_user_approved=True
    res = await engine.tools.execute_tool(
        name="file_operation",
        arguments={"operation": "delete", "source_path": "test.txt"},
        is_user_approved=False,
    )
    assert res.success is False
    assert "Permission Error" in (res.error or "")
    assert res.verified is False


@pytest.mark.asyncio
async def test_scenario_7_honest_failure_reporting(engine: AgentExecutionEngine):
    res = await engine.tools.execute_tool(
        name="read_document",
        arguments={"file_path": "non_existent_file.pdf"},
    )
    assert res.success is False
    assert "File not found" in (res.error or "")
    assert res.verified is False


@pytest.mark.asyncio
async def test_scenario_8_cancellation_support(engine: AgentExecutionEngine):
    prompt = "Nova, open Notepad, create a file called test_cancel.txt and write Testing cancellation."
    analysis = engine.understand_task(prompt)
    plan = engine.create_plan(prompt, analysis)
    
    # Request cancellation before execution
    engine.cancel_execution(plan.plan_id)
    report = await engine.execute_plan(plan)
    assert report.steps_succeeded == 0
    assert any(s["status"] == "cancelled" for s in report.step_results)


@pytest.mark.asyncio
async def test_scenario_9_workspace_security_rejection(engine: AgentExecutionEngine):
    # Attempt path traversal
    attack_prompt = "Examine and read C:/Windows/win.ini please"
    analysis = engine.understand_task(attack_prompt)
    assert analysis["intent"] == TaskIntent.SECURITY_VIOLATION
    
    plan = engine.create_plan(attack_prompt, analysis)
    report = await engine.execute_plan(plan)
    assert report.status == "BLOCKED"
    assert "Security Error: Access Denied" in report.final_output
    assert report.steps_total == 0


@pytest.mark.asyncio
async def test_scenario_10_inference_service_agent_pipeline():
    from app.inference.service import InferenceService
    from app.inference.repository import InferenceRepository
    from app.inference.schemas import ChatInferenceRequest
    
    service = InferenceService(InferenceRepository())
    prompt = "Nova, open Notepad, create a file called meeting.txt and write Tomorrow's meeting is at 10 AM."
    req = ChatInferenceRequest(prompt=prompt)
    
    test_file = BASE_DIR / "meeting.txt"
    try:
        res = await service.execute_chat(req)
        assert res.model == "unified_agent_execution_engine"
        assert res.verification["valid"] is True
        assert res.verification["steps_succeeded"] == 3
        assert test_file.exists() is True
        assert "Tomorrow's meeting is at 10 AM" in test_file.read_text(encoding="utf-8")
        assert "meeting.txt" in res.content
    finally:
        if test_file.exists():
            test_file.unlink()
        service.agent_engine.tools.launcher.terminate_application("notepad")


@pytest.mark.asyncio
async def test_scenario_11_inference_service_security_rejection():
    from app.inference.service import InferenceService
    from app.inference.repository import InferenceRepository
    from app.inference.schemas import ChatInferenceRequest
    
    service = InferenceService(InferenceRepository())
    req = ChatInferenceRequest(prompt="Examine and read C:/Windows/win.ini please")
    res = await service.execute_chat(req)
    
    assert res.model == "unified_agent_execution_engine"
    assert res.verification["valid"] is False
    assert "Security Error: Access Denied" in res.content


@pytest.mark.asyncio
async def test_scenario_12_streaming_service_agent_pipeline():
    from app.inference.service import StreamingService
    from app.inference.repository import InferenceRepository
    
    streaming = StreamingService(InferenceRepository())
    prompt = "Nova, open Notepad, create a file called meeting.txt and write Tomorrow's meeting is at 10 AM."
    
    test_file = BASE_DIR / "meeting.txt"
    try:
        chunks = []
        async for chunk in streaming.stream_chat(prompt):
            chunks.append(chunk["text"])
            
        full_text = "".join(chunks)
        assert "Task Completed Successfully" in full_text
        assert "meeting.txt" in full_text
        assert test_file.exists() is True
    finally:
        if test_file.exists():
            test_file.unlink()
        streaming.agent_engine.tools.launcher.terminate_application("notepad")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


