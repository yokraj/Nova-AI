"""Manual Validation script for the Intelligent Planner & Decomposition Engine.
"""

import asyncio
from app.ai.planner.configuration import MultiAgentPlannerConfiguration
from app.ai.planner.planner import LocalPlannerEngine
from app.ai.planner.models import PlanningRequest, DependencyGraph, Dependency, Task
from app.ai.planner.dependency_graph import DependencyGraphManager
from app.ai.agents.registry import AgentRegistry
from app.ai.agents.models import AgentMetadata, AgentDescriptor, AgentCapability
from app.ai.agents.event_bus import EventBus
from app.ai.planner.health import PlannerHealthMonitor

async def main():
    print("========================================")
    print("Nova AI Planner Validation")
    print("========================================")

    passed = 0
    total = 12

    # Setup core services
    registry = AgentRegistry()
    event_bus = EventBus()
    engine = LocalPlannerEngine(registry=registry, event_bus=event_bus)

    # Pre-register some mock agent
    meta = AgentMetadata(
        id="specialist_auth",
        name="Auth Agent",
        type="auth",
        capabilities=[AgentCapability(name="authentication", description="Handles auth")]
    )
    desc = AgentDescriptor(class_path="app.ai.agents.implementations.mock_agent.MockAgent")
    registry.register(desc, meta)

    request = PlanningRequest(request_id="manual_session_id", goal="Build an ERP software CRM system")
    response = await engine.plan(request)

    # Stage 1 Goal Analysis
    try:
        assert response.status == "success"
        print(f"Stage 1 Goal Analysis PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 1 Goal Analysis FAIL ({str(err)})")

    # Stage 2 Task Tree
    try:
        assert response.task_tree.total_nodes > 1
        print(f"Stage 2 Task Tree PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 2 Task Tree FAIL ({str(err)})")

    # Stage 3 DAG
    try:
        assert len(response.dependency_graph.nodes) > 1
        print(f"Stage 3 DAG PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 3 DAG FAIL ({str(err)})")

    # Stage 4 Cycle Detection
    try:
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
        try:
            manager.detect_cycles()
            print(f"Stage 4 Cycle Detection FAIL (missed cycle)")
        except Exception:
            print(f"Stage 4 Cycle Detection PASS")
            passed += 1
    except Exception as err:
        print(f"Stage 4 Cycle Detection FAIL ({str(err)})")

    # Stage 5 Optimization
    try:
        assert response.metrics.optimization_ratio > 0.0
        print(f"Stage 5 Optimization PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 5 Optimization FAIL ({str(err)})")

    # Stage 6 Scheduling
    try:
        assert len(response.execution_plan.batches) > 0
        print(f"Stage 6 Scheduling PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 6 Scheduling FAIL ({str(err)})")

    # Stage 7 Capability Matching
    try:
        test_task = list(response.dependency_graph.nodes.values())[0]
        matches = engine.matcher.find_matches(test_task)
        print(f"Stage 7 Capability Matching PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 7 Capability Matching FAIL ({str(err)})")

    # Stage 8 Agent Selection
    try:
        has_auth_assignment = False
        for node in response.dependency_graph.nodes.values():
            if node.assignment and node.assignment.agent_id == "specialist_auth":
                has_auth_assignment = True
                break
        assert has_auth_assignment is True
        print(f"Stage 8 Agent Selection PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 8 Agent Selection FAIL ({str(err)})")

    # Stage 9 Recovery
    try:
        assert len(response.execution_plan.recovery_plans) > 0
        print(f"Stage 9 Recovery PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 9 Recovery FAIL ({str(err)})")

    # Stage 10 Event Bus
    try:
        event_registered = []
        async def mock_listener(goal_id: str) -> None:
            event_registered.append(goal_id)
        event_bus.subscribe("PlanningCompleted", mock_listener)
        request.force_replanning = True
        await engine.plan(request)
        assert len(event_registered) > 0
        print(f"Stage 10 Event Bus PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 10 Event Bus FAIL ({str(err)})")

    # Stage 11 Memory
    try:
        await engine.memory.store_plan("session_test", "Goal desc test", "Plan sum test")
        print(f"Stage 11 Memory PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 11 Memory FAIL ({str(err)})")

    # Stage 12 Health
    try:
        monitor = PlannerHealthMonitor(
            engine,
            engine.analyzer,
            engine.dag_builder,
            engine.scheduler,
            engine.optimizer,
            engine.memory,
            event_bus,
            registry
        )
        health = await monitor.check_health()
        assert health["status"] == "healthy"
        print(f"Stage 12 Health PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 12 Health FAIL ({str(err)})")

    await engine.shutdown()

    print(f"\nStages Passed")
    print(f"{passed} / {total}")
    if passed == total:
        print("\nPlanner Healthy")
    else:
        print("\nPlanner Unhealthy")

if __name__ == "__main__":
    asyncio.run(main())
