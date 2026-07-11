"""Unit tests for the NovaOrchestrator coordination system.

Verifies intent classification, planning step splits/merges, agent selection,
permissions checking, scheduler and communication bus routing, and response aggregation.
"""

import asyncio
from typing import Any, Dict, List
import uuid
import pytest

from app.agents import (
    AgentCapability,
    AgentContext,
    AgentDescriptor,
    AgentMetadata,
    AgentPermission,
    AgentRegistry,
    AgentResult,
    BaseAgent,
)
from app.agents.bus import RoutingService
from app.agents.permissions import PermissionManager, PermissionPolicy, PolicyEffect, PolicyDuration, ResourceType
from app.agents.scheduler import AgentScheduler
from app.ai.gateway.ai_gateway import AIGateway
from app.ai.models import ChatResponse, PromptMessage, FinishReason
from app.orchestrator import (
    NovaOrchestrator,
    IntentType,
    IntentClassifier,
    TaskPlanner,
    AgentSelector,
    ResponseBuilder,
)


class DummyAIGateway(AIGateway):
    """Mock AI Gateway stub for orchestrator testing."""

    def __init__(self) -> None:
        pass

    async def chat(self, request: Any, **kwargs: Any) -> ChatResponse:
        content = "CHAT"
        prompt_content = request.messages[-1].content.lower()
        if "code" in prompt_content:
            content = "CODE"
        elif "search" in prompt_content:
            content = "SEARCH"
        return ChatResponse(
            message=PromptMessage(role="assistant", content=content),
            finish_reason=FinishReason.STOP,
            model="llama3",
            provider="ollama",
        )


class DummyOrchestrationAgent(BaseAgent):
    """Mock agent implementation for orchestrator checking."""

    async def initialize(self) -> None:
        pass

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        return AgentResult(
            success=True,
            response=f"Handled: {prompt}",
            metadata={"agent": "dummy"},
            execution_time=0.05,
        )

    async def shutdown(self) -> None:
        pass

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok"}


@pytest.fixture
def orchestrator_setup() -> NovaOrchestrator:
    """Fixture to build orchestrator with all integrated platform layers."""
    registry = AgentRegistry()
    
    # Register ChatAgent
    meta_chat = AgentMetadata(
        name="ChatAgent",
        description="Handles chat prompts",
        capabilities=[AgentCapability.CHAT],
    )
    agent_chat = DummyOrchestrationAgent(meta_chat)
    registry.register(agent_chat)

    # Register CodeAgent with NETWORK permission requirement
    meta_code = AgentMetadata(
        name="CodeAgent",
        description="Handles code prompts",
        capabilities=[AgentCapability.CODE],
        permissions=[AgentPermission.NETWORK],
    )
    agent_code = DummyOrchestrationAgent(meta_code)
    desc_code = AgentDescriptor(
        id=meta_code.id,
        name="CodeAgent",
        description="Handles code prompts",
        capabilities=[AgentCapability.CODE],
        permissions=[AgentPermission.NETWORK],
        priority=200,
    )
    registry.register(agent_code, desc_code)

    # Setup Permissions, Bus, Scheduler, and Mock Gateway
    # Allow code agent network access by policy
    policy_allow = PermissionPolicy(
        policy_id="allow_network",
        agent_id=str(meta_code.id),
        permission=AgentPermission.NETWORK,
        resource_type=ResourceType.NETWORK,
        resource_pattern="*",
        effect=PolicyEffect.ALLOW,
        duration=PolicyDuration.PERMANENT,
    )
    permission_manager = PermissionManager(registry, policies=[policy_allow])

    routing_service = RoutingService(registry)
    scheduler = AgentScheduler(routing_service)
    gateway = DummyAIGateway()

    return NovaOrchestrator(
        registry=registry,
        permission_manager=permission_manager,
        scheduler=scheduler,
        routing_service=routing_service,
        gateway=gateway,
    )


@pytest.mark.anyio
async def test_intent_classification(orchestrator_setup: NovaOrchestrator) -> None:
    """Verifies that IntentClassifier categorizes prompts correctly."""
    classifier = orchestrator_setup.classifier

    # Keyword check
    assert await classifier.classify("Write Python code") == IntentType.CODE
    assert await classifier.classify("Search Google") == IntentType.SEARCH

    # Mock gateway query check
    assert await classifier.classify("Write code script") == IntentType.CODE
    assert await classifier.classify("Ordinary prompt query") == IntentType.CHAT

    assert await classifier.confidence("Write Python code") == 0.95
    assert await classifier.confidence("Ordinary prompt query") == 0.70


def test_task_planning_and_splitting() -> None:
    """Verifies that TaskPlanner plans, splits, and merges steps."""
    planner = TaskPlanner()

    # Create plan
    plan = planner.create_plan(IntentType.CODE, "Write python script")
    assert len(plan) == 2
    assert plan[0]["id"] == "write_code"
    assert plan[1]["id"] == "test_code"

    # Split task step
    split_steps = planner.split(plan[0])
    assert len(split_steps) == 2
    assert split_steps[0]["id"] == "write_code_part1"

    # Merge task outcomes
    task_outcomes = [
        {"id": "write_code_part1", "success": True, "output": "code written"},
        {"id": "write_code_part2", "success": True, "output": "code tested"},
    ]
    merged = planner.merge(task_outcomes)
    assert merged["success"] is True
    assert "code written" in merged["output"]
    assert "code tested" in merged["output"]


def test_agent_selector(orchestrator_setup: NovaOrchestrator) -> None:
    """Verifies Selector finds, ranks, and resolves fallbacks."""
    selector = orchestrator_setup.selector

    # Select candidates
    candidates = selector.select(IntentType.CODE)
    assert "CodeAgent" in candidates

    # Rank checks
    ranked = selector.rank(["ChatAgent", "CodeAgent"])
    # CodeAgent priority was 200, ChatAgent default was 100. CodeAgent should be ranked first.
    assert ranked[0] == "CodeAgent"

    # Fallback check
    assert selector.fallback(IntentType.UNKNOWN) == "ChatAgent"


@pytest.mark.anyio
async def test_orchestrator_process_coordination(orchestrator_setup: NovaOrchestrator) -> None:
    """Verifies process coordinates selection, permission checks, scheduling, and formatting."""
    orchestrator = orchestrator_setup
    conversation_id = uuid.uuid4()

    # Execution 1: Chat Prompt (no permissions needed)
    res_chat = await orchestrator.process("Hello assistant!", conversation_id)
    assert "Orchestrator Execution Status: Success" in res_chat
    assert "Handled: Hello assistant!" in res_chat
    assert len(orchestrator.state.completed) == 1

    # Execution 2: Code Prompt (requires network permission check, allowed by perm policy)
    res_code = await orchestrator.process("Write Python code", conversation_id)
    assert "Orchestrator Execution Status: Success" in res_code
    assert "Handled: Write code for: Write Python code" in res_code
    # Plan has 2 steps: write_code and test_code
    assert len(orchestrator.state.completed) == 3  # (1 from chat + 2 from code)


def test_orchestrator_response_building() -> None:
    """Verifies response builders aggregate summaries and format markdown."""
    builder = ResponseBuilder()

    responses = [
        {"success": True, "output": "Step 1 done"},
        {"success": True, "output": "Step 2 done"},
    ]

    aggregated = builder.aggregate(responses)
    assert aggregated["success"] is True
    assert aggregated["count"] == 2

    summary = builder.summarize(aggregated)
    assert "Step 1 done" in summary
    assert "Step 2 done" in summary

    formatted = builder.format(summary, format_type="markdown")
    assert formatted.startswith("### Response")
