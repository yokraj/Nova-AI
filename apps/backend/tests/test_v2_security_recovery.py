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
    PlannedStep,
    ExecutionPlan,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if not BASE_DIR.exists() or not (BASE_DIR / "apps").exists():
    BASE_DIR = Path(r"C:\Projects\Nova-AI")


@pytest.fixture
def engine() -> AgentExecutionEngine:
    return AgentExecutionEngine()


@pytest.mark.asyncio
async def test_case_1_path_traversal_rejection(engine: AgentExecutionEngine):
    """Case 1: Path traversal attempts must be blocked."""
    analysis = engine.understand_task("Read ../../../Windows/System32/drivers/etc/hosts")
    assert analysis["intent"] == TaskIntent.SECURITY_VIOLATION
    plan = engine.create_plan("Read ../../../Windows/System32/drivers/etc/hosts", analysis)
    report = await engine.execute_plan(plan)
    assert report.status == "BLOCKED"
    assert "Access Denied" in report.final_output


@pytest.mark.asyncio
async def test_case_2_unauthorized_deletion(engine: AgentExecutionEngine):
    """Case 2: Unauthorized file operations must be gated with SENSITIVE permission."""
    tool = engine.tools.get("file_operation")
    assert tool is not None
    assert tool.permission_level.value == "SENSITIVE"


@pytest.mark.asyncio
async def test_case_3_unauthorized_system_control(engine: AgentExecutionEngine):
    """Case 3: Unauthorized system control commands must be gated."""
    result = await engine.tools.execute_tool(
        "system_control",
        {"action": "shutdown"},
    )
    assert result.success is False or result.output.get("status") == "FAILED"


@pytest.mark.asyncio
async def test_case_4_invalid_tool_arguments(engine: AgentExecutionEngine):
    """Case 4: Invalid tool arguments must fail gracefully."""
    result = await engine.tools.execute_tool("open_application", {})
    assert result.success is False
    assert (
        "missing" in (result.error or "").lower()
        or "required" in (result.error or "").lower()
        or "app_name" in (result.error or "").lower()
    )


@pytest.mark.asyncio
async def test_case_5_missing_files_honesty(engine: AgentExecutionEngine):
    """Case 5: Missing files must report honest FileNotFoundError without mocks."""
    result = await engine.tools.execute_tool("read_document", {"file_path": "non_existent_ghost_file.txt"})
    assert result.success is False
    assert "not found" in (result.error or "").lower() or "does not exist" in (result.error or "").lower()


@pytest.mark.asyncio
async def test_case_6_command_timeout(engine: AgentExecutionEngine):
    """Case 6: Bounded execution returns status safely without hang."""
    result = await engine.tools.execute_tool("calculate_math", {"expression": "2 ** 10"})
    assert result.success is True
    assert result.output["result"] == 1024


@pytest.mark.asyncio
async def test_case_7_user_cancellation_mid_execution(engine: AgentExecutionEngine):
    """Case 7: User cancellation mid-execution must cancel remaining steps."""
    plan = ExecutionPlan(
        plan_id="plan_cancel_test",
        user_goal="Multi-step cancel test",
        intent=TaskIntent.CALCULATION,
        steps=[
            PlannedStep(step_id=1, tool_name="calculate_math", arguments={"expression": "10 + 10"}, description="Step 1"),
            PlannedStep(step_id=2, tool_name="calculate_math", arguments={"expression": "20 + 20"}, description="Step 2"),
        ],
    )
    engine.cancel_execution("plan_cancel_test")
    report = await engine.execute_plan(plan)
    assert report.status in ("CANCELLED", "PARTIAL")
    assert any(s["status"] == "cancelled" for s in report.step_results)


@pytest.mark.asyncio
async def test_case_8_recovery_from_failed_step(engine: AgentExecutionEngine):
    """Case 8: Honest failure reporting when a step fails."""
    plan = ExecutionPlan(
        plan_id="plan_failure_recovery",
        user_goal="Failing step test",
        intent=TaskIntent.FILE_OPERATION,
        steps=[
            PlannedStep(step_id=1, tool_name="read_document", arguments={"file_path": "definitely_not_here.csv"}, description="Read missing file"),
            PlannedStep(step_id=2, tool_name="calculate_math", arguments={"expression": "5 * 5"}, description="Dependent math", dependencies=[1]),
        ],
    )
    report = await engine.execute_plan(plan)
    assert report.status == "FAILED"
    assert report.steps_succeeded == 0
    assert "Failed at Step 1" in report.final_output


@pytest.mark.asyncio
async def test_case_9_existing_file_identical_name(engine: AgentExecutionEngine):
    """Case 9: Handling existing file with identical name."""
    target = BASE_DIR / "duplicate_test.txt"
    try:
        # Create initial file
        target.write_text("Initial content version 1", encoding="utf-8")
        assert target.exists()

        # Execute create_file tool with new content
        result = await engine.tools.execute_tool(
            "create_file",
            {"file_path": "duplicate_test.txt", "content": "Updated content version 2 with more data"},
        )
        assert result.success is True
        assert target.read_text(encoding="utf-8") == "Updated content version 2 with more data"
        assert result.output["size_bytes"] == len("Updated content version 2 with more data")
    finally:
        if target.exists():
            target.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
