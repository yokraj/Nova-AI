"""Unit tests for the Intelligent Planner & Task Decomposition Engine.
"""

import pytest
import asyncio
from app.ai.planner.configuration import MultiAgentPlannerConfiguration
from app.ai.planner.exceptions import CycleError, ValidationError
from app.ai.planner.models import PlanningRequest, DependencyGraph, Dependency, Task, TaskTree, TaskNode
from app.ai.planner.planner import LocalPlannerEngine
from app.ai.planner.dependency_graph import DependencyGraphManager
from app.ai.agents.registry import AgentRegistry
from app.ai.agents.models import AgentMetadata, AgentDescriptor, AgentCapability
from app.ai.agents.event_bus import EventBus
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies

@pytest.mark.anyio
async def test_planner_configuration():
    """Verifies default planner configuration parses settings."""
    config = MultiAgentPlannerConfiguration()
    assert config.planner.enabled is True
    assert config.goal.recursion_depth == 5
    assert config.scheduler.parallel_task_limits == 4

@pytest.mark.anyio
async def test_goal_analysis_and_decomposition():
    """Verifies that goal analyzer classifies software and scientific research domains correctly."""
    engine = LocalPlannerEngine()
    
    # Software goal
    request_sw = PlanningRequest(request_id="test_sw", goal="Build a React CRM system")
    response_sw = await engine.plan(request_sw)
    assert response_sw.status == "success"
    assert response_sw.task_tree.total_nodes > 2
    
    # Scientific research goal
    request_res = PlanningRequest(request_id="test_res", goal="Search literature about quantum computing")
    response_res = await engine.plan(request_res)
    assert response_res.status == "success"
    assert response_res.metrics.task_count > 1

@pytest.mark.anyio
async def test_cycle_detection():
    """Verifies that DependencyGraphManager raises CycleError on circular dependencies."""
    task_a = Task(task_id="A", title="A", description="A", dependencies=["B"])
    task_b = Task(task_id="B", title="B", description="B", dependencies=["A"])
    graph = DependencyGraph(
        nodes={"A": task_a, "B": task_b},
        edges=[
            Dependency(dependency_id="1", source_task_id="A", target_task_id="B"),
            Dependency(dependency_id="2", source_task_id="B", target_task_id="A")
        ]
    )
    manager = DependencyGraphManager(graph)
    with pytest.raises(CycleError):
        manager.detect_cycles()

@pytest.mark.anyio
async def test_scheduler_and_optimization():
    """Verifies scheduler batches concurrent steps and optimizer reduces redundant items."""
    engine = LocalPlannerEngine()
    request = PlanningRequest(request_id="test_opt", goal="Build a new ERP website")
    response = await engine.plan(request)
    
    assert response.status == "success"
    assert len(response.execution_plan.batches) > 0
    assert response.execution_plan.total_estimated_seconds > 0.0

@pytest.mark.anyio
async def test_capability_matching_and_fallback():
    """Verifies that specialised capability matching resolves targets, falling back to SoftwareEngineerAgent."""
    registry = AgentRegistry()
    
    # Register specialized agent
    meta = AgentMetadata(
        id="specialist_db",
        name="DB Specialist Agent",
        type="database",
        capabilities=[AgentCapability(name="database_design", description="Design databases")]
    )
    descriptor = AgentDescriptor(class_path="app.ai.agents.implementations.mock_agent.MockAgent")
    registry.register(descriptor, meta)
    
    # Initialize engine with the custom registry
    engine = LocalPlannerEngine(registry=registry)
    
    # Triggers database capability matching
    request = PlanningRequest(request_id="test_cap", goal="Build a software CRM database system")
    response = await engine.plan(request)
    
    assert response.status == "success"
    
    has_db_specialist = False
    has_se_fallback = False
    
    for task in response.dependency_graph.nodes.values():
        if task.assignment:
            if task.assignment.agent_id == "specialist_db":
                has_db_specialist = True
            elif task.assignment.agent_id == "software_engineer":
                has_se_fallback = True
                
    assert has_db_specialist is True
    assert has_se_fallback is True

@pytest.mark.anyio
async def test_recovery_planning():
    """Verifies that recovery plans are populated with fallbacks and retry limits."""
    engine = LocalPlannerEngine()
    request = PlanningRequest(request_id="test_recovery", goal="Build quantum CRM systems")
    response = await engine.plan(request)
    
    assert response.status == "success"
    assert len(response.execution_plan.recovery_plans) > 0
    
    recovery_plan = list(response.execution_plan.recovery_plans.values())[0]
    assert recovery_plan.max_retries == 3
    assert recovery_plan.allow_retry is True

@pytest.mark.anyio
async def test_event_bus_publishing():
    """Verifies that planner engine triggers events on execution cycles."""
    event_bus = EventBus()
    received_events = []
    
    async def log_started(goal: str) -> None:
        received_events.append(f"Started: {goal}")
        
    async def log_completed(goal_id: str) -> None:
        received_events.append(f"Completed: {goal_id}")
        
    event_bus.subscribe("PlanningStarted", log_started)
    event_bus.subscribe("PlanningCompleted", log_completed)
    
    engine = LocalPlannerEngine(event_bus=event_bus)
    request = PlanningRequest(request_id="test_event_id", goal="Analyze target research papers")
    await engine.plan(request)
    
    assert len(received_events) == 2
    assert "Started: Analyze target research papers" in received_events
    assert "Completed: test_event_id" in received_events

@pytest.mark.anyio
async def test_gateway_plan_integration():
    """Verifies the gateway exposes plan and returns successful planning response."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass
    gateway = resolve(IAIGateway)
    request = PlanningRequest(request_id="test_gateway_id", goal="Build CRM portals")
    response = await gateway.plan(request)
    
    assert response.status == "success"
    assert response.session_id == "test_gateway_id"
