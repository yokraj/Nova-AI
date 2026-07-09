"""Unit tests for the Nova AI Workflow Engine.

Verifies planners, event buses, parallel execution levels, step retries,
timeouts, and cancellation flows.
"""

import asyncio
from unittest.mock import AsyncMock
import pytest

from app.automation import (
    DependencyGraph,
    EventBus,
    ExecutionPlanner,
    Workflow,
    WorkflowContext,
    WorkflowExecutionEngine,
    WorkflowStatus,
    WorkflowStep,
)


def test_planner_cycle_detection() -> None:
    """Verifies that dependency graphs detect circular dependencies loops."""
    # Step A -> Step B -> Step A (Cycle!)
    step_a = WorkflowStep(
        id="step_a",
        name="Step A",
        capability="text",
        dependencies=["step_b"],
    )
    step_b = WorkflowStep(
        id="step_b",
        name="Step B",
        capability="text",
        dependencies=["step_a"],
    )

    steps = [step_a, step_b]
    graph = DependencyGraph(steps)
    assert graph.has_cycles() is True

    with pytest.raises(ValueError):
        ExecutionPlanner.plan(steps)


def test_planner_ordering_levels() -> None:
    """Verifies step grouping layers for parallelizable runs."""
    #   A (no dep)   B (no dep)
    #       \       /
    #           C (depends on A, B)
    #           |
    #           D (depends on C)
    step_a = WorkflowStep(id="step_a", name="A", capability="text")
    step_b = WorkflowStep(id="step_b", name="B", capability="text")
    step_c = WorkflowStep(
        id="step_c", name="C", capability="text", dependencies=["step_a", "step_b"]
    )
    step_d = WorkflowStep(
        id="step_d", name="D", capability="text", dependencies=["step_c"]
    )

    steps = [step_a, step_b, step_c, step_d]
    levels = ExecutionPlanner.plan(steps)

    assert len(levels) == 3
    # Level 0 can run A and B in parallel
    assert {s.id for s in levels[0]} == {"step_a", "step_b"}
    # Level 1 runs C
    assert [s.id for s in levels[1]] == ["step_c"]
    # Level 2 runs D
    assert [s.id for s in levels[2]] == ["step_d"]


@pytest.mark.anyio
async def test_event_bus_pub_sub() -> None:
    """Verifies Event Bus subscriber callbacks execution."""
    event_bus = EventBus()
    received_data = []

    async def mock_callback(data: dict) -> None:
        received_data.append(data)

    event_bus.subscribe("test_event", mock_callback)
    await event_bus.publish("test_event", {"status": "ok"})

    assert len(received_data) == 1
    assert received_data[0]["status"] == "ok"


@pytest.mark.anyio
async def test_execution_engine_success() -> None:
    """Verifies successful concurrent execution and parameter mapping mappings."""
    event_bus = EventBus()
    engine = WorkflowExecutionEngine(event_bus)

    # Context setup
    context = WorkflowContext(variables={"input_val": "Nova"})

    # Setup steps: step_a maps input_val -> resolves output -> maps context output_val
    step_a = WorkflowStep(
        id="step_a",
        name="A",
        capability="text",
        input_mapping={"text_in": "input_val"},
        output_mapping={"output": "output_val"},
    )

    workflow = Workflow(
        id="wf_1",
        name="Test Workflow",
        steps=[step_a],
    )

    result = await engine.execute(workflow, context)
    assert result.status == WorkflowStatus.COMPLETED
    assert "output_val" in result.variables
    assert "Nova" in result.variables["output_val"]


@pytest.mark.anyio
async def test_execution_step_retry() -> None:
    """Verifies transient failed steps recover using configured retry loops."""
    event_bus = EventBus()

    # Step runner failing once, succeeding on retry attempt
    attempts = 0

    async def failing_runner(step, context):
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise Exception("Transient network issue")
        return {"output": "Success"}

    engine = WorkflowExecutionEngine(event_bus, step_runner=failing_runner)
    context = WorkflowContext()

    step_a = WorkflowStep(
        id="step_a",
        name="A",
        capability="text",
        retry_limit=1,  # Allows 1 retry (2 total attempts)
        output_mapping={"output": "res"},
    )

    workflow = Workflow(id="wf_1", name="WF", steps=[step_a])
    result = await engine.execute(workflow, context)

    assert result.status == WorkflowStatus.COMPLETED
    assert result.variables["res"] == "Success"
    assert attempts == 2


@pytest.mark.anyio
async def test_execution_step_timeout() -> None:
    """Verifies execution time limits trigger execution timeouts exceptions."""
    event_bus = EventBus()

    async def slow_runner(step, context):
        await asyncio.sleep(0.5)
        return {"output": "Succeeded slowly"}

    engine = WorkflowExecutionEngine(event_bus, step_runner=slow_runner)
    context = WorkflowContext()

    step_a = WorkflowStep(
        id="step_a",
        name="A",
        capability="text",
        timeout_seconds=0.1,  # Short timeout limit
    )

    workflow = Workflow(id="wf_1", name="WF", steps=[step_a])
    result = await engine.execute(workflow, context)

    assert result.status == WorkflowStatus.FAILED
    assert "TimeoutError" in str(result.error_message) or "A" in str(
        result.error_message
    )


@pytest.mark.anyio
async def test_execution_engine_cancellation() -> None:
    """Verifies execution aborts when cancellation token is raised."""
    event_bus = EventBus()

    async def cancel_runner(step, context):
        context.is_cancelled = True
        return {"output": "Aborted"}

    engine = WorkflowExecutionEngine(event_bus, step_runner=cancel_runner)
    context = WorkflowContext()

    step_a = WorkflowStep(id="step_a", name="A", capability="text")
    step_b = WorkflowStep(
        id="step_b", name="B", capability="text", dependencies=["step_a"]
    )

    workflow = Workflow(id="wf_1", name="WF", steps=[step_a, step_b])
    result = await engine.execute(workflow, context)

    assert result.status == WorkflowStatus.CANCELLED
    # Step B should remain pending since execution was aborted at Level 1 (Step A)
    assert workflow.steps[1].status == WorkflowStatus.PENDING
